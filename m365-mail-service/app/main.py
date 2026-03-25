import secrets
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

app = FastAPI(title="Open WebUI M365 Mail Integration", version="0.4.0")


class DeviceFlowStartRequest(BaseModel):
    email: Optional[str] = None


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
