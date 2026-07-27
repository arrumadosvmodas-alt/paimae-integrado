"""Integracao nao-oficial com o ClipEscola (app de comunicacao escolar).

O ClipEscola nao oferece API para responsaveis - apenas login pessoal via QR
Code (like WhatsApp Web) numa aplicacao web JSF/PrimeFaces cuja navegacao
depende de postbacks AJAX (nao e uma API JSON, nem links GET simples). Por
isso o acesso automatizado usa Playwright (navegador headless), reproduzindo
os mesmos cliques que um usuario faria, em vez de tentar reimplementar o
protocolo interno de ViewState do PrimeFaces via HTTP puro - abordagem mais
fragil a mudancas de layout, mas muito mais fragil ainda tentar replicar o
protocolo JSF diretamente.

Isto NAO e uma integracao oficial. Uso por conta e risco do responsavel, com
login e sessao pessoais dele. Ver riscos documentados no plano da feature.
"""
import base64
import json
import logging
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_str, encrypt_str
from app.models.child import Child
from app.models.integration import ClipEscolaAccount
from app.models.pedagogy import SchoolSchedule
from app.core.config import settings
from app.services.llm import get_llm_service

logger = logging.getLogger(__name__)

LOGIN_URL = "https://www.clipescola.com.br/acesso/login-responsavel.xhtml"
DASHBOARD_URL_FRAGMENT = "mobile/index.xhtml"

llm_service = get_llm_service(settings.google_gemini_api_key)


class ClipEscolaAuthError(Exception):
    """Sessao expirada ou nunca pareada - requer novo QR Code."""


def _load_storage_state(account: ClipEscolaAccount) -> dict | None:
    if not account.session_cookie_encrypted:
        return None
    return json.loads(decrypt_str(account.session_cookie_encrypted))


def _save_storage_state(account: ClipEscolaAccount, storage_state: dict) -> None:
    account.session_cookie_encrypted = encrypt_str(json.dumps(storage_state))


def _get_or_create_account(db: Session, guardian_id: UUID, child_id: UUID) -> ClipEscolaAccount:
    account = db.scalar(
        select(ClipEscolaAccount).where(
            ClipEscolaAccount.guardian_id == guardian_id,
            ClipEscolaAccount.child_id == child_id,
        )
    )
    if not account:
        account = ClipEscolaAccount(
            guardian_id=guardian_id,
            child_id=child_id,
            status="pending_pairing",
        )
        db.add(account)
        db.flush()
    return account


# Pareamento por QR Code exige manter o MESMO navegador/aba aberto entre o
# momento de gerar o QR e o momento de checar se o celular ja escaneou -
# fechar e reabrir com o cookie salvo nao e suficiente (o ClipEscola nao
# reconhece o pareamento se a sessao original ja foi encerrada). Por isso
# usamos a API assincrona do Playwright (compativel com o loop de eventos
# do FastAPI/uvicorn) e mantemos a pagina viva em memoria entre requisicoes,
# em vez da API sincrona usada no restante deste modulo.
_active_pairings: dict[str, dict] = {}
_PAIRING_TTL_SECONDS = 300  # 5 minutos - depois disso descartamos a tentativa


async def _close_pairing_session(account_key: str) -> None:
    session = _active_pairings.pop(account_key, None)
    if not session:
        return
    try:
        await session["browser"].close()
    except Exception:
        logger.exception("Erro ao fechar sessao de pareamento ClipEscola (conta %s)", account_key)
    try:
        await session["playwright"].stop()
    except Exception:
        pass


async def _cleanup_stale_pairings() -> None:
    now = datetime.utcnow()
    stale_keys = [
        key for key, session in _active_pairings.items()
        if (now - session["created_at"]).total_seconds() > _PAIRING_TTL_SECONDS
    ]
    for key in stale_keys:
        await _close_pairing_session(key)


async def start_pairing(db: Session, guardian_id: UUID, child_id: UUID) -> dict:
    """Abre uma sessao nova no ClipEscola e retorna o QR Code para o
    responsavel escanear com o celular (app oficial dele). O navegador fica
    aberto em memoria ate o pareamento ser confirmado ou expirar."""
    from playwright.async_api import async_playwright

    account = _get_or_create_account(db, guardian_id, child_id)
    account_key = str(account.id)

    await _cleanup_stale_pairings()
    await _close_pairing_session(account_key)  # descarta tentativa anterior pendente, se houver

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(LOGIN_URL, wait_until="networkidle")

    qr_element = page.locator("img[src*='qrcode' i], canvas, svg").first
    qr_bytes = await qr_element.screenshot()

    _active_pairings[account_key] = {
        "playwright": playwright,
        "browser": browser,
        "context": context,
        "page": page,
        "created_at": datetime.utcnow(),
    }

    account.status = "pending_pairing"
    db.flush()

    return {
        "account_id": account_key,
        "qr_image_base64": base64.b64encode(qr_bytes).decode(),
    }


# A propria pagina de login faz polling via AJAX (POST repetido para a
# mesma URL, padrao PrimeFaces p:poll - confirmado inspecionando o trafego
# de rede real) para detectar quando o celular autoriza o pareamento, e se
# redireciona sozinha quando isso acontece. Por isso NUNCA recarregamos
# (page.reload/goto) enquanto aguardamos: um reload destroi esse mecanismo
# de polling interno (reinicia a pagina do zero) e ainda troca o QR Code
# por um novo (confirmado via teste direto). So observamos o estado atual
# da mesma pagina, sempre aberta, deixando o JS dela fazer o trabalho.


async def check_pairing_status(db: Session, account: ClipEscolaAccount) -> dict:
    """Verifica se a propria pagina (mantida aberta, com seu polling AJAX
    interno rodando) ja se redirecionou para o dashboard apos o celular
    autorizar o pareamento. Nunca recarrega a pagina."""
    account_key = str(account.id)
    session = _active_pairings.get(account_key)

    if not session:
        # Sem navegador vivo em memoria (nunca pareou, ja pareou antes, ou o
        # processo reiniciou) - mantem o status atual em vez de inventar um.
        return {"status": account.status, "qr_image_base64": None}

    page = session["page"]
    try:
        paired = DASHBOARD_URL_FRAGMENT in page.url
    except Exception:
        logger.exception("Erro ao verificar pareamento ClipEscola (conta %s)", account_key)
        paired = False

    if paired:
        storage_state = await session["context"].storage_state()
        _save_storage_state(account, storage_state)
        account.status = "active"
        account.last_synced_at = datetime.utcnow()
        db.flush()
        await _close_pairing_session(account_key)

    return {"status": account.status, "qr_image_base64": None}


def _extract_category_messages(page, category_name: str) -> list[str]:
    """Na pagina da categoria (feed.xhtml) ja aberta, extrai o texto de cada
    recado. A pagina mostra 'Tudo vazio!...' quando nao ha recados."""
    body_text = page.locator("body").inner_text()
    if "Tudo vazio" in body_text:
        return []

    # Heuristica: cada recado aparece como bloco de texto separado por
    # timestamps (HH:MM). Sem um seletor CSS estavel conhecido (app nao
    # documentado), agrupamos linhas nao vazias, uma "mensagem" por bloco
    # entre timestamps consecutivos.
    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    messages: list[str] = []
    buffer: list[str] = []
    for line in lines:
        buffer.append(line)
        if _looks_like_timestamp(line):
            text = " ".join(buffer[:-1]).strip()
            if text and text.lower() not in {"agenda", category_name.lower()}:
                messages.append(text)
            buffer = []
    return messages


def _looks_like_timestamp(line: str) -> bool:
    import re

    return bool(re.fullmatch(r"\d{1,2}:\d{2}", line))


def sync_agenda(db: Session, account: ClipEscolaAccount) -> dict:
    """Le a Agenda de Recados do ClipEscola, usa IA para extrair conteudo de
    estudo (assunto/data) e alimenta o pipeline pedagogico existente via
    `SchoolSchedule(source='clip_escola')`."""
    from playwright.sync_api import sync_playwright

    storage_state = _load_storage_state(account)
    if not storage_state or account.status != "active":
        return {"status": "needs_reauth", "message": "Conta nunca pareada ou nao ativa."}

    all_messages: list[str] = []
    session_valid = True

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_state)
        page = context.new_page()
        page.goto(f"https://www.clipescola.com.br/acesso/{DASHBOARD_URL_FRAGMENT}", wait_until="networkidle")

        if DASHBOARD_URL_FRAGMENT not in page.url:
            session_valid = False
        else:
            page.get_by_text("AGENDA DE RECADOS", exact=False).first.click()
            page.wait_for_load_state("networkidle")

            category_names = page.locator("text=/Direção|Secretaria|Recepção|Financeiro|Coordenação|Biblioteca/").all_inner_texts()
            for category_name in category_names:
                try:
                    page.get_by_text(category_name, exact=True).first.click()
                    page.wait_for_load_state("networkidle")
                    all_messages.extend(_extract_category_messages(page, category_name))
                    page.go_back()
                    page.wait_for_load_state("networkidle")
                except Exception:
                    logger.exception("Falha ao ler categoria '%s' do ClipEscola (conta %s)", category_name, account.id)

        updated_state = context.storage_state()
        browser.close()

    _save_storage_state(account, updated_state)

    if not session_valid:
        account.status = "needs_reauth"
        db.flush()
        return {"status": "needs_reauth", "message": "Sessao do ClipEscola expirou."}

    account.status = "active"
    account.last_synced_at = datetime.utcnow()

    if not all_messages:
        db.flush()
        return {"status": "success", "schedules_created": 0, "messages_read": 0}

    entries = llm_service.extract_agenda_entries(all_messages)
    created = _persist_schedule_entries(db, account.child_id, entries)
    db.flush()

    return {"status": "success", "schedules_created": created, "messages_read": len(all_messages)}


def _persist_schedule_entries(db: Session, child_id: UUID, entries: list[dict]) -> int:
    child = db.get(Child, child_id)
    if not child:
        return 0

    created = 0
    for entry in entries:
        raw_date = entry.get("date")
        subject = entry.get("subject")
        if not raw_date or not subject:
            continue
        try:
            entry_date = date.fromisoformat(raw_date)
        except (ValueError, TypeError):
            logger.warning("Data invalida em recado extraido do ClipEscola: %r", raw_date)
            continue

        existing = db.scalar(
            select(SchoolSchedule).where(
                SchoolSchedule.child_id == child_id,
                SchoolSchedule.date == entry_date,
                SchoolSchedule.subject == subject,
                SchoolSchedule.source == "clip_escola",
            )
        )
        if existing:
            continue

        schedule = SchoolSchedule(
            child_id=child_id,
            school_id=child.school_id,
            date=entry_date,
            subject=subject,
            topic=entry.get("topic"),
            source="clip_escola",
            confidence_score=int(float(entry.get("confidence", 0)) * 100),
            status="planned",
            is_active=True,
        )
        db.add(schedule)
        created += 1

    return created
