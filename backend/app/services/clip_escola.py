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


def start_pairing(db: Session, guardian_id: UUID, child_id: UUID) -> dict:
    """Abre uma sessao nova no ClipEscola e retorna o QR Code para o
    responsavel escanear com o celular (app oficial dele)."""
    from playwright.sync_api import sync_playwright

    account = _get_or_create_account(db, guardian_id, child_id)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL, wait_until="networkidle")

        qr_element = page.locator("img[src*='qrcode' i], canvas, svg").first
        qr_bytes = qr_element.screenshot()

        storage_state = context.storage_state()
        browser.close()

    _save_storage_state(account, storage_state)
    account.status = "pending_pairing"
    db.flush()

    return {
        "account_id": str(account.id),
        "qr_image_base64": base64.b64encode(qr_bytes).decode(),
    }


def check_pairing_status(db: Session, account: ClipEscolaAccount) -> str:
    """Reabre a mesma sessao (mesmo cookie) para ver se o celular ja
    escaneou o QR Code e autorizou o pareamento."""
    from playwright.sync_api import sync_playwright

    storage_state = _load_storage_state(account)
    if not storage_state:
        return "pending_pairing"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_state)
        page = context.new_page()
        page.goto(LOGIN_URL, wait_until="networkidle")

        paired = DASHBOARD_URL_FRAGMENT in page.url

        updated_state = context.storage_state()
        browser.close()

    _save_storage_state(account, updated_state)
    account.status = "active" if paired else "pending_pairing"
    if paired:
        account.last_synced_at = datetime.utcnow()
    db.flush()
    return account.status


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
