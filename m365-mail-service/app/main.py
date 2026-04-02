import secrets
import sqlite3
import time
from typing import Any, Dict, List, Optional

import msal
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import get_settings
from .db import (
    init_db,
    insert_oauth_state,
    list_mailboxes,
    pop_oauth_state,
    upsert_mailbox,
    get_mailbox,
)
from .graph import (
    get_access_token,
    graph_get,
    init_device_flow,
    acquire_token_by_device_flow,
)
from . import imap_client
from . import google_workspace_client
from . import calendar_client
from . import teams_client
from . import exact_client
from . import moneybird_client
from .db import upsert_imap_mailbox, upsert_google_workspace_mailbox

app = FastAPI(title="LC Mail & Productivity Service", version="1.0.0")


class DeviceFlowStartRequest(BaseModel):
    email: Optional[str] = None


class GoogleWorkspaceConnectRequest(BaseModel):
    email: str  # Het e-mailadres van de gebruiker (moet in het Google Workspace domein zitten)
    display_name: Optional[str] = None
    service_account_json: str  # De volledige JSON key van het service account


class ImapConnectRequest(BaseModel):
    email: str
    display_name: Optional[str] = None
    imap_host: str
    imap_port: int = 993
    imap_ssl: bool = True
    username: str
    password: str


class SummarizeRequest(BaseModel):
    mailbox_id: int
    message_id: str


class DraftReplyRequest(BaseModel):
    mailbox_id: int
    message_id: str
    tone: Optional[str] = "neutral"


@app.on_event("startup")
def startup() -> None:
    init_db()
    # Maak pending_flows tabel aan als die nog niet bestaat
    import sqlite3, os
    db_path = get_settings().database_path
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_flows (
            device_code TEXT PRIMARY KEY,
            email TEXT,
            started_at REAL NOT NULL,
            expires_at REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _save_pending_flow(device_code: str, email: Optional[str], expires_in: int) -> None:
    import sqlite3
    db_path = get_settings().database_path
    now = time.time()
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO pending_flows (device_code, email, started_at, expires_at) VALUES (?,?,?,?)",
        (device_code, email, now, now + expires_in)
    )
    conn.commit()
    conn.close()


def _get_latest_pending_flow() -> Optional[str]:
    """Geeft de meest recente niet-verlopen device_code terug."""
    import sqlite3
    db_path = get_settings().database_path
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT device_code FROM pending_flows WHERE expires_at > ? ORDER BY started_at DESC LIMIT 1",
        (time.time(),)
    ).fetchone()
    conn.close()
    return row[0] if row else None


def _delete_pending_flow(device_code: str) -> None:
    import sqlite3
    db_path = get_settings().database_path
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM pending_flows WHERE device_code = ?", (device_code,))
    conn.commit()
    conn.close()


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.post("/auth/device/start")
def auth_device_start(payload: DeviceFlowStartRequest) -> Dict[str, Any]:
    """Start device code flow for OAuth login."""
    try:
        flow = init_device_flow()
        expires_in = flow.get("expires_in", 900)

        # Persisteer de flow in SQLite
        _save_pending_flow(flow["device_code"], payload.email, expires_in)

        return {
            "status": "pending",
            "user_code": flow["user_code"],
            "verification_uri": flow["verification_uri"],
            "message": flow.get("message", "To sign in, open the page and enter the code."),
            "expires_in": expires_in,
            "device_code": flow["device_code"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/device/poll")
def auth_device_poll(device_code: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Poll for completion of device code flow. Zonder device_code: gebruik de laatste bekende."""
    # Als geen device_code meegegeven, gebruik de meest recente
    if not device_code:
        device_code = _get_latest_pending_flow()
        if not device_code:
            return {"status": "no_pending", "message": "Geen actieve koppeling gevonden. Start eerst een nieuwe koppeling."}

    try:
        result = acquire_token_by_device_flow(device_code)

        if result is None:
            return {"status": "pending", "message": "Waiting for user to complete login..."}

        access_token = result["access_token"]
        profile = graph_get(access_token, "/me", params={"$select": "id,displayName,mail,userPrincipalName"})
        email = profile.get("mail") or profile.get("userPrincipalName")

        _delete_pending_flow(device_code)

        mailbox_id = upsert_mailbox(
            email=email,
            display_name=profile.get("displayName"),
            tenant_id=get_settings().tenant_id,
            token=result,
        )

        return {
            "status": "connected",
            "mailbox": {
                "id": mailbox_id,
                "email": email,
                "display_name": profile.get("displayName"),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/auth/device/latest")
def auth_device_latest() -> Dict[str, Any]:
    """Geeft de meest recente actieve device_code terug (voor debugging)."""
    code = _get_latest_pending_flow()
    return {"device_code": code, "has_pending": code is not None}


@app.get("/mailboxes")
def mailboxes() -> Dict[str, Any]:
    return {"mailboxes": list_mailboxes()}


@app.post("/google/connect")
def google_connect(payload: GoogleWorkspaceConnectRequest) -> Dict[str, Any]:
    """
    Koppel een Google Workspace mailbox via service account impersonation.
    Vereist dat de admin eenmalig domain-wide delegation heeft ingeschakeld.
    """
    try:
        verified_email = google_workspace_client.test_connection(
            service_account_json=payload.service_account_json,
            user_email=payload.email,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Google Workspace verbinding mislukt: {str(e)}. "
                   f"Controleer of domain-wide delegation is ingeschakeld en de Gmail API actief is."
        )

    mailbox_id = upsert_google_workspace_mailbox(
        email=payload.email,
        display_name=payload.display_name or verified_email,
        service_account_json=payload.service_account_json,
    )
    return {
        "status": "connected",
        "mailbox": {
            "id": mailbox_id,
            "email": verified_email,
            "display_name": payload.display_name or verified_email,
            "provider": "google",
        },
    }


@app.post("/imap/connect")
def imap_connect(payload: ImapConnectRequest) -> Dict[str, Any]:
    """Koppel een IMAP mailbox. Test verbinding voor opslaan."""
    imap_config = {
        "imap_host": payload.imap_host,
        "imap_port": payload.imap_port,
        "imap_ssl": payload.imap_ssl,
        "username": payload.username,
        "password": payload.password,
    }
    try:
        imap_client.test_connection(imap_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"IMAP verbinding mislukt: {str(e)}")

    mailbox_id = upsert_imap_mailbox(
        email=payload.email,
        display_name=payload.display_name or payload.email,
        imap_host=payload.imap_host,
        imap_port=payload.imap_port,
        imap_ssl=payload.imap_ssl,
        username=payload.username,
        password=payload.password,
    )
    return {
        "status": "connected",
        "mailbox": {
            "id": mailbox_id,
            "email": payload.email,
            "display_name": payload.display_name or payload.email,
            "provider": "imap",
        },
    }


@app.get("/messages")
def messages(
    mailbox_id: int = Query(...),
    top: int = Query(10, ge=1, le=50),
    folder: Optional[str] = Query(None),
    unread_only: bool = Query(False),
) -> Dict[str, Any]:
    mailbox = get_mailbox(mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")

    provider = mailbox.get("provider", "m365")

    if provider == "imap":
        msgs = imap_client.fetch_messages(
            mailbox=mailbox,
            top=top,
            folder=folder or "inbox",
            unread_only=unread_only,
        )
        return {"messages": msgs}

    if provider == "google":
        service_account_json = mailbox.get("imap_config")  # hergebruikt imap_config kolom
        if not service_account_json:
            raise HTTPException(status_code=500, detail="Google service account niet geconfigureerd")
        msgs = google_workspace_client.fetch_messages(
            service_account_json=service_account_json,
            user_email=mailbox["email"],
            top=top,
            folder=folder or "inbox",
            unread_only=unread_only,
        )
        return {"messages": msgs}

    # M365 flow (ongewijzigd)
    access_token = get_access_token(mailbox)
    select_fields = "id,subject,from,receivedDateTime,bodyPreview,importance,isRead,hasAttachments"
    params = {
        "$top": top,
        "$orderby": "receivedDateTime DESC",
        "$select": select_fields,
    }
    if unread_only:
        params["$filter"] = "isRead eq false"
    if folder:
        path = f"/me/mailFolders/{folder}/messages"
    else:
        path = "/me/messages"
    data = graph_get(access_token, path, params=params)
    return {"messages": data.get("value", [])}


def _score_importance(message: Dict[str, Any]) -> Dict[str, Any]:
    score = 30
    reasons: List[str] = []
    importance = (message.get("importance") or "normal").lower()
    if importance == "high":
        score += 40
        reasons.append("Message marked as high importance")
    if message.get("hasAttachments"):
        score += 10
        reasons.append("Has attachments")
    if not message.get("isRead", True):
        score += 10
        reasons.append("Unread message")
    if message.get("subject"):
        subject = message["subject"].lower()
        if any(keyword in subject for keyword in ["invoice", "payment", "urgent", "asap"]):
            score += 10
            reasons.append("Subject contains urgency/finance keyword")
    score = min(score, 100)
    label = "low" if score < 40 else "medium" if score < 70 else "high"
    if not reasons:
        reasons.append("No strong urgency signals detected")
    return {"score": score, "label": label, "reasons": reasons}


def _dutch_summary_prompt(message: Dict[str, Any]) -> str:
    subject = message.get("subject") or "(geen onderwerp)"
    body = message.get("body", {}).get("content") or message.get("bodyPreview") or ""
    return (
        "Vat het volgende e-mailbericht samen in het Nederlands in 3-5 zinnen. "
        "Noem actiepunten, deadlines en beslissingen.\n\n"
        f"Onderwerp: {subject}\n"
        f"Bericht: {body}"
    )


@app.post("/summarize_message")
def summarize_message(payload: SummarizeRequest) -> Dict[str, Any]:
    mailbox = get_mailbox(payload.mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    access_token = get_access_token(mailbox)
    data = graph_get(
        access_token,
        f"/me/messages/{payload.message_id}",
        params={"$select": "id,subject,from,receivedDateTime,body,bodyPreview,importance,isRead,hasAttachments"},
    )
    return {
        "message": data,
        "importance": _score_importance(data),
        "summary_prompt_nl": _dutch_summary_prompt(data),
        "note": "Generate the actual summary using your LLM of choice.",
    }


@app.post("/draft_reply")
def draft_reply(payload: DraftReplyRequest) -> Dict[str, Any]:
    mailbox = get_mailbox(payload.mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    access_token = get_access_token(mailbox)
    data = graph_get(
        access_token,
        f"/me/messages/{payload.message_id}",
        params={"$select": "id,subject,from,receivedDateTime,bodyPreview,body"},
    )
    sender = data.get("from", {}).get("emailAddress", {}).get("name") or "there"
    subject = data.get("subject") or "(no subject)"
    body_preview = data.get("bodyPreview") or ""
    tone = payload.tone or "neutral"

    suggestions = [
        {
            "subject": f"Re: {subject}",
            "body_text": (
                f"Hi {sender},\n\n"
                f"Thanks for your message. I reviewed the details and will get back to you with next steps. "
                f"In the meantime, please let me know if anything else is needed.\n\n"
                f"Best regards,"
            ),
        },
        {
            "subject": f"Re: {subject}",
            "body_text": (
                f"Hello {sender},\n\n"
                f"Appreciate the update. Based on your note, I will follow up shortly. "
                f"If you need a quicker response, please flag the priority.\n\n"
                f"Regards,"
            ),
        },
    ]

    return {
        "message_context": {
            "id": data.get("id"),
            "subject": subject,
            "from": data.get("from"),
            "body_preview": body_preview,
        },
        "tone": tone,
        "draft_suggestions": suggestions,
        "note": "These are plain-text suggestions only; no drafts are created in Microsoft 365.",
    }


# ─── CALENDAR ─────────────────────────────────────────────────────────────────

@app.get("/calendar/events")
def calendar_events(
    mailbox_id: int = Query(...),
    days_ahead: int = Query(1, ge=1, le=7),
    max_results: int = Query(10, ge=1, le=50),
) -> Dict[str, Any]:
    """Haal agenda-items op voor een mailbox (M365 of Google Workspace)."""
    mailbox = get_mailbox(mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    try:
        events = calendar_client.fetch_events(mailbox, days_ahead=days_ahead, max_results=max_results)
        return {"events": events, "mailbox": mailbox.get("email"), "days_ahead": days_ahead}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calendar/all")
def calendar_all(
    days_ahead: int = Query(1, ge=1, le=7),
    max_results: int = Query(10, ge=1, le=50),
) -> Dict[str, Any]:
    """Haal agenda-items op van ALLE gekoppelde mailboxen."""
    boxes = list_mailboxes()
    all_events = []
    errors = []
    for mailbox in boxes:
        try:
            events = calendar_client.fetch_events(
                get_mailbox(mailbox["id"]), days_ahead=days_ahead, max_results=max_results
            )
            for e in events:
                e["mailbox"] = mailbox.get("email")
            all_events.extend(events)
        except Exception as ex:
            errors.append(f"{mailbox.get('email')}: {str(ex)}")

    # Sorteer op starttijd
    all_events.sort(key=lambda x: x.get("start", ""))
    return {"events": all_events, "errors": errors}


# ─── TEAMS ────────────────────────────────────────────────────────────────────

@app.get("/teams/messages")
def teams_messages(
    mailbox_id: int = Query(...),
    hours_back: int = Query(24, ge=1, le=168),
) -> Dict[str, Any]:
    """Haal recente Teams berichten op voor een mailbox."""
    mailbox = get_mailbox(mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    if mailbox.get("provider", "m365") != "m365":
        raise HTTPException(status_code=400, detail="Teams is alleen beschikbaar voor M365 mailboxen")
    try:
        messages = teams_client.fetch_teams_messages(mailbox, hours_back=hours_back)
        return {"teams_messages": messages, "mailbox": mailbox.get("email"), "hours_back": hours_back}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── EXACT ONLINE ─────────────────────────────────────────────────────────────

class ExactConnectRequest(BaseModel):
    client_id: str
    client_secret: str
    authorization_code: str
    division: int


@app.post("/exact/connect")
def exact_connect(payload: ExactConnectRequest) -> Dict[str, Any]:
    """Koppel Exact Online via authorization code (eenmalig door admin)."""
    settings = get_settings()
    try:
        result = exact_client.connect_exact(
            client_id=payload.client_id,
            client_secret=payload.client_secret,
            authorization_code=payload.authorization_code,
            division=payload.division,
            db_path=settings.database_path,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/exact/invoices")
def exact_invoices(max_results: int = Query(10, ge=1, le=50)) -> Dict[str, Any]:
    """Haal openstaande verkoopfacturen op uit Exact Online."""
    settings = get_settings()
    try:
        invoices = exact_client.get_open_invoices(settings.database_path, max_results)
        return {"invoices": invoices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exact/receivables")
def exact_receivables(max_results: int = Query(10, ge=1, le=50)) -> Dict[str, Any]:
    """Haal openstaande debiteuren op uit Exact Online."""
    settings = get_settings()
    try:
        items = exact_client.get_open_receivables(settings.database_path, max_results)
        return {"receivables": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exact/transactions")
def exact_transactions(max_results: int = Query(10, ge=1, le=50)) -> Dict[str, Any]:
    """Haal recente boekingen op uit Exact Online."""
    settings = get_settings()
    try:
        items = exact_client.get_recent_transactions(settings.database_path, max_results)
        return {"transactions": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── MONEYBIRD ────────────────────────────────────────────────────────────────

class MoneybirdConnectRequest(BaseModel):
    api_token: str
    administration_id: Optional[str] = None


@app.post("/moneybird/connect")
def moneybird_connect(payload: MoneybirdConnectRequest) -> Dict[str, Any]:
    """Koppel Moneybird via persoonlijk API token."""
    import sqlite3
    try:
        admin = moneybird_client.test_connection(payload.api_token)
        administration_id = payload.administration_id or str(admin.get("id"))

        # Sla token op in config tabel
        db_path = get_settings().database_path
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS moneybird_config (
                id INTEGER PRIMARY KEY,
                api_token TEXT,
                administration_id TEXT
            )
        """)
        conn.execute("DELETE FROM moneybird_config WHERE id = 1")
        conn.execute(
            "INSERT INTO moneybird_config VALUES (1, ?, ?)",
            (payload.api_token, administration_id)
        )
        conn.commit()
        conn.close()

        return {
            "status": "connected",
            "administration": admin.get("name"),
            "administration_id": administration_id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Moneybird koppeling mislukt: {str(e)}")


def _get_moneybird_config():
    import sqlite3
    db_path = get_settings().database_path
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM moneybird_config WHERE id = 1").fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=400, detail="Moneybird niet gekoppeld. Gebruik POST /moneybird/connect eerst.")
    return dict(row)


@app.get("/moneybird/invoices")
def moneybird_invoices(max_results: int = Query(10, ge=1, le=50)) -> Dict[str, Any]:
    """Haal onbetaalde facturen op uit Moneybird."""
    config = _get_moneybird_config()
    try:
        invoices = moneybird_client.get_unpaid_invoices(
            config["api_token"], config["administration_id"], max_results
        )
        return {"invoices": invoices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/moneybird/estimates")
def moneybird_estimates(max_results: int = Query(5, ge=1, le=20)) -> Dict[str, Any]:
    """Haal recente offertes op uit Moneybird."""
    config = _get_moneybird_config()
    try:
        estimates = moneybird_client.get_recent_estimates(
            config["api_token"], config["administration_id"], max_results
        )
        return {"estimates": estimates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# ─── EXACT ONLINE SETUP FLOW ─────────────────────────────────────────────────

class ExactSetupStartRequest(BaseModel):
    client_id: str
    client_secret: str
    division: int


class ExactCallbackReceiveRequest(BaseModel):
    code: str
    state: Optional[str] = None


@app.post("/exact/setup/start")
def exact_setup_start(payload: ExactSetupStartRequest) -> Dict[str, Any]:
    """Sla Exact setup-config op en geef de OAuth URL terug."""
    import urllib.parse, time
    settings = get_settings()
    conn = sqlite3.connect(settings.database_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS exact_pending_setup (
            id INTEGER PRIMARY KEY,
            client_id TEXT,
            client_secret TEXT,
            division INTEGER,
            created_at REAL
        )
    """)
    conn.execute("DELETE FROM exact_pending_setup")
    conn.execute(
        "INSERT INTO exact_pending_setup VALUES (1, ?, ?, ?, ?)",
        (payload.client_id, payload.client_secret, payload.division, time.time())
    )
    conn.commit()
    conn.close()

    redirect_uri = "https://callback.localcompute.nl/"
    params = urllib.parse.urlencode({
        "client_id": payload.client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "force_login": "0",
    })
    auth_url = f"https://start.exactonline.nl/api/oauth2/auth?{params}"
    return {
        "status": "pending",
        "auth_url": auth_url,
        "instructie": f"Open deze URL in uw browser: {auth_url}"
    }


@app.post("/exact/callback/receive")
def exact_callback_receive(payload: ExactCallbackReceiveRequest) -> Dict[str, Any]:
    """Ontvangt de authorization code van de PHP relay op callback.localcompute.nl."""
    settings = get_settings()
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM exact_pending_setup ORDER BY created_at DESC LIMIT 1").fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=400, detail="Geen actieve Exact setup. Start opnieuw via POST /exact/setup/start.")

    config = dict(row)
    try:
        exact_client.connect_exact(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            authorization_code=payload.code,
            division=config["division"],
            db_path=settings.database_path,
        )
        return {"status": "connected", "message": "Exact Online succesvol gekoppeld!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exact/callback")
def exact_callback_get(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
) -> Any:
    """OAuth GET callback — directe browser redirect."""
    if error:
        raise HTTPException(status_code=400, detail=f"Exact OAuth fout: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Geen code ontvangen")
    return exact_callback_receive(ExactCallbackReceiveRequest(code=code, state=state))


# ── Google OAuth endpoints ─────────────────────────────────────────────────────

from . import google_oauth_client

class GoogleOAuthSetupRequest(BaseModel):
    client_id: str
    client_secret: str


class GoogleOAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None


@app.post("/google/oauth/setup")
def google_oauth_setup(payload: GoogleOAuthSetupRequest) -> Dict[str, Any]:
    """
    Sla Google OAuth credentials op en geef de login URL terug.
    Stap 1 van Google koppeling.
    """
    import secrets
    state = secrets.token_urlsafe(16)

    google_oauth_client.save_google_oauth_config(
        settings.database_path,
        payload.client_id,
        payload.client_secret,
    )

    auth_url = google_oauth_client.get_auth_url(payload.client_id, state)

    # Sla state op voor CSRF verificatie
    db = sqlite3.connect(settings.database_path)
    db.execute("""
        CREATE TABLE IF NOT EXISTS google_oauth_states (
            state TEXT PRIMARY KEY,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        )
    """)
    db.execute("INSERT OR REPLACE INTO google_oauth_states (state) VALUES (?)", (state,))
    db.commit()
    db.close()

    return {
        "status": "ready",
        "auth_url": auth_url,
        "instructie": (
            f"Open deze URL in je browser om in te loggen met Google:\n{auth_url}\n\n"
            "Na inloggen word je doorgestuurd naar callback.localcompute.nl/google. "
            "Kopieer die volledige URL en stuur hem naar /google/oauth/callback."
        )
    }


@app.get("/google/oauth/callback")
def google_oauth_callback_get(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
) -> Any:
    """OAuth GET callback — directe browser redirect vanuit Google."""
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth fout: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Geen code ontvangen van Google")
    return google_oauth_callback_receive(GoogleOAuthCallbackRequest(code=code, state=state))


@app.post("/google/oauth/callback")
def google_oauth_callback_receive(payload: GoogleOAuthCallbackRequest) -> Dict[str, Any]:
    """Voltooi Google OAuth — wissel code in voor tokens en sla mailbox op."""
    import time

    config = google_oauth_client.get_google_oauth_config(settings.database_path)
    if not config:
        raise HTTPException(status_code=400, detail="Google OAuth niet geconfigureerd. Start via /google/oauth/setup.")

    try:
        tokens = google_oauth_client.exchange_code(
            config["client_id"], config["client_secret"], payload.code
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token exchange mislukt: {str(e)}")

    try:
        userinfo = google_oauth_client.get_userinfo(tokens["access_token"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gebruikersinfo ophalen mislukt: {str(e)}")

    email = userinfo.get("email", "")
    display_name = userinfo.get("name", email)

    # Voeg expires_at toe
    tokens["expires_at"] = time.time() + tokens.get("expires_in", 3600)

    google_oauth_client.save_google_tokens(
        settings.database_path, email, display_name, tokens
    )

    return {
        "status": "connected",
        "email": email,
        "display_name": display_name,
        "message": f"Google account van {display_name} ({email}) succesvol gekoppeld!"
    }


@app.post("/google/oauth/complete")
def google_oauth_complete(payload: GoogleOAuthCallbackRequest) -> Dict[str, Any]:
    """Alias voor /google/oauth/callback — voor gebruik vanuit Setup Assistent."""
    return google_oauth_callback_receive(payload)
