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
from app.models.pedagogy import PedagogicalMaterial, SchoolSchedule
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


def _extract_clips_entries(page) -> list[str]:
    """Na aba 'Clips', agrupa o texto de cada post em um bloco. O layout real
    (confirmado por captura de tela do usuario) e um feed de posts, cada um
    com categoria (ex: 'Avisos e Circulares'), 'Postado por <autor>', uma
    data dd/mm/aaaa e hora, seguidos de titulo e corpo da mensagem - tudo
    isso agrupado sob rotulos relativos de dia (ex: 'Ontem') que NAO sao
    confiaveis como data exata. Por isso usamos a linha 'Postado por ...'
    como inicio de cada bloco (post), e extraimos a data real de dentro do
    bloco depois, via regex, em vez de depender de um separador de data."""
    body_text = page.locator("body").inner_text()
    if "Tudo vazio" in body_text:
        return []

    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in lines:
        if line.lower().startswith("postado por"):
            if current is not None:
                blocks.append(current)
            current = [line]
        elif current is not None:
            current.append(line)
        # linhas antes do primeiro post (rotulo de dia, categoria) sao descartadas
    if current is not None:
        blocks.append(current)
    return ["\n".join(block) for block in blocks]


def _match_material(db: Session, school_id: UUID, book_name: str | None) -> PedagogicalMaterial | None:
    """Tenta casar o nome do livro citado na agenda diaria com um material
    ja cadastrado na escola. Sem um identificador estavel (ISBN raramente e
    citado na agenda), usa correspondencia por titulo (substring, case
    insensitive) - suficiente para o caso comum de o nome bater
    aproximadamente com o titulo cadastrado."""
    if not book_name or not book_name.strip():
        return None
    normalized = book_name.strip()
    return db.scalar(
        select(PedagogicalMaterial).where(
            PedagogicalMaterial.school_id == school_id,
            PedagogicalMaterial.is_active.is_(True),
            PedagogicalMaterial.title.ilike(f"%{normalized}%"),
        )
    )


def sync_agenda(db: Session, account: ClipEscolaAccount) -> dict:
    """Le os posts visiveis na aba 'Clips' do ClipEscola, usa IA para
    extrair conteudo de estudo (materia/livro/paginacao) dos que forem
    didaticos e alimenta o pipeline pedagogico existente via
    `SchoolSchedule(source='clip_escola')`, tentando vincular ao material
    (livro) ja cadastrado na escola."""
    from playwright.sync_api import sync_playwright

    storage_state = _load_storage_state(account)
    if not storage_state or account.status != "active":
        return {"status": "needs_reauth", "message": "Conta nunca pareada ou nao ativa."}

    clips_blocks: list[str] = []
    session_valid = True

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_state)
        page = context.new_page()
        page.goto(f"https://www.clipescola.com.br/acesso/{DASHBOARD_URL_FRAGMENT}", wait_until="networkidle")

        if DASHBOARD_URL_FRAGMENT not in page.url:
            session_valid = False
        else:
            try:
                page.get_by_text("Clips", exact=False).first.click()
                page.wait_for_load_state("networkidle")
                clips_blocks = _extract_clips_entries(page)
            except Exception:
                logger.exception("Falha ao ler aba 'Clips' do ClipEscola (conta %s)", account.id)

        updated_state = context.storage_state()
        browser.close()

    _save_storage_state(account, updated_state)

    if not session_valid:
        account.status = "needs_reauth"
        db.flush()
        return {"status": "needs_reauth", "message": "Sessao do ClipEscola expirou."}

    account.status = "active"
    account.last_synced_at = datetime.utcnow()

    if not clips_blocks:
        db.flush()
        return {"status": "success", "schedules_created": 0, "clips_read": 0}

    daily_entries = llm_service.extract_daily_agenda_entries(clips_blocks)
    created = _persist_schedule_entries(db, account.child_id, daily_entries)
    db.flush()

    return {
        "status": "success",
        "schedules_created": created,
        "clips_read": len(clips_blocks),
    }


def _post_date(block: str) -> str | None:
    """Extrai a data 'oficial' do post (a que aparece perto de 'Postado
    por ... dd/mm/aaaa ... HH:MM', tipicamente nas primeiras linhas do
    bloco). So cai para o resto do bloco se nao achar nada no cabecalho,
    ja que o CORPO da mensagem pode citar outras datas sem relacao (ex: a
    data de um evento futuro mencionado no texto do aviso)."""
    import re

    lines = block.splitlines()
    header = "\n".join(lines[:5])
    match = re.search(r"\d{2}/\d{2}/\d{4}", header)
    if match:
        return match.group(0)
    match = re.search(r"\d{2}/\d{2}/\d{4}", block)
    return match.group(0) if match else None


def _block_matches_date(block: str, target_date: date) -> bool:
    return _post_date(block) == target_date.strftime("%d/%m/%Y")


def _go_to_previous_period(page) -> bool:
    """Tenta clicar num controle de navegacao 'anterior' na aba Clips (seta,
    botao ou link com nome comum em datepickers PrimeFaces) para carregar um
    periodo anterior. Retorna False se nao achar nenhum controle."""
    selectors = [
        "button:has-text('Anterior')",
        "a:has-text('Anterior')",
        "[aria-label*='anterior' i]",
        "[aria-label*='previous' i]",
        ".ui-datepicker-prev",
        "button:has-text('<')",
        "a:has-text('<')",
    ]
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if locator.count() > 0:
                locator.click()
                page.wait_for_load_state("networkidle")
                return True
        except Exception:
            continue
    return False


def _scroll_for_more_content(page) -> bool:
    """A aba 'Clips' e um feed (confirmado por captura de tela do usuario),
    sem controles visiveis de paginacao - o padrao comum nesse tipo de lista
    mobile e carregar posts mais antigos ao rolar. Usado como alternativa
    quando nao ha botao de 'anterior'. Retorna False se a rolagem nao mudou
    o conteudo visivel (chegamos ao fim do historico)."""
    before = page.locator("body").inner_text()
    try:
        page.mouse.wheel(0, 4000)
        page.wait_for_timeout(800)
        page.wait_for_load_state("networkidle")
    except Exception:
        return False
    after = page.locator("body").inner_text()
    return after != before


def _advance_clips_page(page) -> bool:
    return _go_to_previous_period(page) or _scroll_for_more_content(page)


_DATE_LOOKUP_MAX_ATTEMPTS = 12  # limite de "paginas para tras" antes de desistir


def find_agenda_for_date(db: Session, account: ClipEscolaAccount, target_date: date) -> dict:
    """Busca na aba 'Clips' o conteudo de um dia especifico informado pelo
    responsavel - usado quando a sincronizacao automatica nao trouxe nada
    para aquele dia (ex: dia fora da janela padrao exibida pelo app, ou a
    sincronizacao automatica ainda nao rodou). Navega para tras nas paginas
    da aba Clips ate achar o dia pedido ou esgotar as tentativas."""
    from playwright.sync_api import sync_playwright

    storage_state = _load_storage_state(account)
    if not storage_state or account.status != "active":
        return {"status": "needs_reauth", "message": "Conta nunca pareada ou nao ativa."}

    found_block: str | None = None
    session_valid = True

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_state)
        page = context.new_page()
        page.goto(f"https://www.clipescola.com.br/acesso/{DASHBOARD_URL_FRAGMENT}", wait_until="networkidle")

        if DASHBOARD_URL_FRAGMENT not in page.url:
            session_valid = False
        else:
            try:
                page.get_by_text("Clips", exact=False).first.click()
                page.wait_for_load_state("networkidle")

                for _ in range(_DATE_LOOKUP_MAX_ATTEMPTS):
                    blocks = _extract_clips_entries(page)
                    match = next((b for b in blocks if _block_matches_date(b, target_date)), None)
                    if match:
                        found_block = match
                        break
                    if not _advance_clips_page(page):
                        break
            except Exception:
                logger.exception(
                    "Falha ao buscar data especifica (%s) na aba 'Clips' do ClipEscola (conta %s)",
                    target_date, account.id,
                )

        updated_state = context.storage_state()
        browser.close()

    _save_storage_state(account, updated_state)

    if not session_valid:
        account.status = "needs_reauth"
        db.flush()
        return {"status": "needs_reauth", "message": "Sessao do ClipEscola expirou."}

    account.status = "active"
    db.flush()

    if not found_block:
        return {"status": "not_found", "date": target_date.isoformat()}

    entries = llm_service.extract_daily_agenda_entries([found_block])
    created = _persist_schedule_entries(db, account.child_id, entries)
    db.flush()

    return {
        "status": "success",
        "date": target_date.isoformat(),
        "schedules_created": created,
        "raw_text": found_block,
        "entries": entries,
    }


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

        material = _match_material(db, child.school_id, entry.get("book"))

        schedule = SchoolSchedule(
            child_id=child_id,
            school_id=child.school_id,
            date=entry_date,
            subject=subject,
            topic=entry.get("topic"),
            material_id=material.id if material else None,
            page_start=entry.get("page_start"),
            page_end=entry.get("page_end"),
            source="clip_escola",
            confidence_score=int(float(entry.get("confidence", 0)) * 100),
            status="planned",
            is_active=True,
        )
        db.add(schedule)
        created += 1

    return created
