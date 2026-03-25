"""
Google Workspace mail client voor lc-mail-service.
Gebruikt Service Account met Domain-wide Delegation om Gmail te lezen namens gebruikers.
Vereist: google-auth + google-api-python-client in requirements.txt
"""

import base64
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _get_credentials(service_account_json: str, user_email: str):
    """Maak service account credentials aan met impersonation voor user_email."""
    from google.oauth2 import service_account

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    info = json.loads(service_account_json)
    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES
    )
    # Impersonate de opgegeven gebruiker
    delegated = credentials.with_subject(user_email)
    return delegated


def test_connection(service_account_json: str, user_email: str) -> str:
    """
    Test of de service account toegang heeft tot de mailbox van user_email.
    Geeft display_name terug bij succes, gooit exception bij fout.
    """
    from googleapiclient.discovery import build

    creds = _get_credentials(service_account_json, user_email)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    profile = service.users().getProfile(userId="me").execute()
    return profile.get("emailAddress", user_email)


def _parse_header(headers: list, name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def _parse_from(from_str: str) -> Dict[str, Any]:
    """Parse 'Name <email>' format."""
    import re
    match = re.match(r'"?([^"<]*)"?\s*<?([^>]*)>?', from_str.strip())
    if match:
        name = match.group(1).strip().strip('"')
        address = match.group(2).strip()
        return {"emailAddress": {"name": name or address, "address": address}}
    return {"emailAddress": {"name": from_str, "address": from_str}}


def _decode_body(payload: dict) -> str:
    """Haal plain text body op uit Gmail message payload."""
    def _decode_part(part: dict) -> str:
        mime = part.get("mimeType", "")
        if mime == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                try:
                    return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
                except Exception:
                    return ""
        if "parts" in part:
            for p in part["parts"]:
                result = _decode_part(p)
                if result:
                    return result
        return ""

    return _decode_part(payload)


def fetch_messages(
    service_account_json: str,
    user_email: str,
    top: int = 10,
    folder: str = "inbox",
    unread_only: bool = False,
) -> List[Dict[str, Any]]:
    """
    Haal berichten op via Gmail API met service account impersonation.
    Geeft lijst van dicts in M365 Graph API formaat.
    """
    from googleapiclient.discovery import build

    creds = _get_credentials(service_account_json, user_email)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    # Build query
    label_ids = []
    if folder.lower() == "inbox":
        label_ids = ["INBOX"]
    
    query_parts = []
    if unread_only:
        query_parts.append("is:unread")
    
    q = " ".join(query_parts) if query_parts else None

    list_kwargs = {
        "userId": "me",
        "maxResults": top,
    }
    if label_ids:
        list_kwargs["labelIds"] = label_ids
    if q:
        list_kwargs["q"] = q

    list_result = service.users().messages().list(**list_kwargs).execute()
    message_refs = list_result.get("messages", [])

    results = []
    for ref in message_refs:
        try:
            msg = service.users().messages().get(
                userId="me",
                id=ref["id"],
                format="full",
                metadataHeaders=["Subject", "From", "Date"]
            ).execute()

            headers = msg.get("payload", {}).get("headers", [])
            subject = _parse_header(headers, "Subject")
            from_str = _parse_header(headers, "From")
            date_str = _parse_header(headers, "Date")

            label_names = msg.get("labelIds", [])
            is_read = "UNREAD" not in label_names
            has_attachments = any(
                p.get("filename") for p in msg.get("payload", {}).get("parts", [])
            )

            # Parse date
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(date_str)
                received_dt = dt.isoformat()
            except Exception:
                received_dt = datetime.now(timezone.utc).isoformat()

            # Body preview
            body_text = _decode_body(msg.get("payload", {}))
            body_preview = body_text[:200].strip().replace("\r\n", " ").replace("\n", " ")
            if not body_preview:
                body_preview = msg.get("snippet", "")[:200]

            results.append({
                "id": msg["id"],
                "subject": subject,
                "from": _parse_from(from_str),
                "receivedDateTime": received_dt,
                "bodyPreview": body_preview,
                "isRead": is_read,
                "hasAttachments": has_attachments,
                "importance": "normal",
            })
        except Exception:
            continue

    return results
