"""
IMAP client voor lc-mail-service.
Haalt berichten op via stdlib imaplib — geen extra dependencies.
Output formaat is identiek aan M365 Graph API response zodat /messages endpoint unified werkt.
"""

import email
import email.header
import imaplib
import json
import re
from datetime import datetime, timezone
from email.utils import parseaddr, parsedate_to_datetime
from typing import Any, Dict, List, Optional


def _decode_header(value: str) -> str:
    """Decode MIME encoded-word strings (b64 / quoted-printable)."""
    if not value:
        return ""
    parts = email.header.decode_header(value)
    result = []
    for raw, charset in parts:
        if isinstance(raw, bytes):
            try:
                result.append(raw.decode(charset or "utf-8", errors="replace"))
            except (LookupError, UnicodeDecodeError):
                result.append(raw.decode("utf-8", errors="replace"))
        else:
            result.append(raw)
    return "".join(result)


def _parse_from(from_str: str) -> Dict[str, Any]:
    name, address = parseaddr(_decode_header(from_str))
    return {"emailAddress": {"name": name or address, "address": address}}


def _get_plain_text(msg: email.message.Message) -> str:
    """Haal plain text body op (eerste text/plain part)."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                try:
                    return part.get_payload(decode=True).decode(charset, errors="replace")
                except Exception:
                    return ""
    else:
        if msg.get_content_type() == "text/plain":
            charset = msg.get_content_charset() or "utf-8"
            try:
                return msg.get_payload(decode=True).decode(charset, errors="replace")
            except Exception:
                return ""
    return ""


def _has_attachments(msg: email.message.Message) -> bool:
    for part in msg.walk():
        if part.get_content_disposition() in ("attachment", "inline"):
            if part.get_filename():
                return True
    return False


def _parse_date(date_str: str) -> str:
    """Converteer email Date header naar ISO 8601."""
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def _connect(imap_config: Dict[str, Any]) -> imaplib.IMAP4:
    host = imap_config["imap_host"]
    port = int(imap_config.get("imap_port", 993))
    ssl = imap_config.get("imap_ssl", True)
    username = imap_config["username"]
    password = imap_config["password"]

    if ssl:
        conn = imaplib.IMAP4_SSL(host, port)
    else:
        conn = imaplib.IMAP4(host, port)

    conn.login(username, password)
    return conn


def test_connection(imap_config: Dict[str, Any]) -> None:
    """Test IMAP verbinding en authenticatie. Gooit exception bij fout."""
    conn = _connect(imap_config)
    conn.logout()


def fetch_messages(
    mailbox: Dict[str, Any],
    top: int = 10,
    folder: str = "inbox",
    unread_only: bool = False,
) -> List[Dict[str, Any]]:
    """
    Haal berichten op via IMAP.
    Geeft lijst van dicts in M365 Graph API formaat.
    """
    imap_config = json.loads(mailbox["imap_config"])

    imap_folder = "INBOX" if folder.lower() == "inbox" else folder

    conn = _connect(imap_config)
    try:
        conn.select(imap_folder, readonly=True)

        if unread_only:
            status, data = conn.search(None, "UNSEEN")
        else:
            status, data = conn.search(None, "ALL")

        if status != "OK" or not data[0]:
            return []

        uids = data[0].split()
        # Meest recente eerst, max `top`
        uids = uids[-top:]
        uids.reverse()

        results = []
        for uid in uids:
            try:
                status, msg_data = conn.fetch(uid, "(RFC822)")
                if status != "OK":
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                subject = _decode_header(msg.get("Subject", ""))
                from_hdr = msg.get("From", "")
                date_hdr = msg.get("Date", "")
                flags_status, flags_data = conn.fetch(uid, "(FLAGS)")
                is_read = False
                if flags_status == "OK" and flags_data[0]:
                    flags_str = flags_data[0].decode() if isinstance(flags_data[0], bytes) else str(flags_data[0])
                    is_read = "\\Seen" in flags_str

                plain_body = _get_plain_text(msg)
                body_preview = plain_body[:200].strip().replace("\r\n", " ").replace("\n", " ")

                results.append({
                    "id": uid.decode() if isinstance(uid, bytes) else str(uid),
                    "subject": subject,
                    "from": _parse_from(from_hdr),
                    "receivedDateTime": _parse_date(date_hdr),
                    "bodyPreview": body_preview,
                    "isRead": is_read,
                    "hasAttachments": _has_attachments(msg),
                    "importance": "normal",
                })
            except Exception:
                continue

        return results

    finally:
        try:
            conn.logout()
        except Exception:
            pass
