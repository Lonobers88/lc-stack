"""
Google OAuth 2.0 client voor lc-mail-service.
Gebruikt Authorization Code Flow zodat gebruikers via browser kunnen inloggen.

Vereist in Google Cloud Console:
1. Project aanmaken
2. Gmail API + Google Calendar API inschakelen
3. OAuth 2.0 Client ID aanmaken (type: Web application)
4. Redirect URI toevoegen: https://callback.localcompute.nl/google
5. Client ID + Secret opslaan in de DB via /google/oauth/setup
"""

import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
REDIRECT_URI = "https://callback.localcompute.nl/google/"


# ── Config opslag ──────────────────────────────────────────────────────────────

def save_google_oauth_config(db_path: str, client_id: str, client_secret: str) -> None:
    """Sla Google OAuth client credentials op in de DB."""
    c = sqlite3.connect(db_path)
    c.execute("""
        CREATE TABLE IF NOT EXISTS google_oauth_config (
            id INTEGER PRIMARY KEY,
            client_id TEXT NOT NULL,
            client_secret TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("DELETE FROM google_oauth_config")
    c.execute("INSERT INTO google_oauth_config (client_id, client_secret) VALUES (?, ?)",
              (client_id, client_secret))
    c.commit()
    c.close()


def get_google_oauth_config(db_path: str) -> Optional[Dict[str, str]]:
    """Haal Google OAuth config op uit de DB."""
    c = sqlite3.connect(db_path)
    try:
        row = c.execute("SELECT client_id, client_secret FROM google_oauth_config LIMIT 1").fetchone()
        return {"client_id": row[0], "client_secret": row[1]} if row else None
    except Exception:
        return None
    finally:
        c.close()


def save_google_tokens(db_path: str, email: str, display_name: str, tokens: dict) -> None:
    """Sla Google tokens op in mailboxes tabel."""
    from .db import upsert_google_oauth_mailbox
    upsert_google_oauth_mailbox(
        db_path=db_path,
        email=email,
        display_name=display_name,
        tokens=json.dumps(tokens),
    )


# ── OAuth flow ─────────────────────────────────────────────────────────────────

def get_auth_url(client_id: str, state: str) -> str:
    """Genereer de Google OAuth login URL."""
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",  # forceer refresh token
        "state": state,
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def exchange_code(client_id: str, client_secret: str, code: str) -> Dict[str, Any]:
    """Wissel authorization code in voor tokens."""
    resp = requests.post(GOOGLE_TOKEN_URL, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_userinfo(access_token: str) -> Dict[str, Any]:
    """Haal gebruikersinfo op via het access token."""
    resp = requests.get(GOOGLE_USERINFO_URL,
                        headers={"Authorization": f"Bearer {access_token}"},
                        timeout=10)
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> Dict[str, Any]:
    """Ververs een verlopen access token."""
    resp = requests.post(GOOGLE_TOKEN_URL, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_valid_token(db_path: str, email: str) -> str:
    """Haal een geldig access token op, ververs indien nodig."""
    c = sqlite3.connect(db_path)
    row = c.execute(
        "SELECT token_data FROM mailboxes WHERE email=? AND provider='google'", (email,)
    ).fetchone()
    c.close()
    if not row:
        raise ValueError(f"Google mailbox {email} niet gevonden")

    tokens = json.loads(row[0])
    # Check of token verlopen is (Google tokens ~1 uur geldig)
    expires_at = tokens.get("expires_at", 0)
    if time.time() < expires_at - 60:
        return tokens["access_token"]

    # Ververs
    config = get_google_oauth_config(db_path)
    if not config:
        raise ValueError("Google OAuth niet geconfigureerd")
    new_tokens = refresh_access_token(
        config["client_id"], config["client_secret"], tokens["refresh_token"]
    )
    tokens["access_token"] = new_tokens["access_token"]
    tokens["expires_at"] = time.time() + new_tokens.get("expires_in", 3600)

    c = sqlite3.connect(db_path)
    c.execute("UPDATE mailboxes SET token_data=? WHERE email=? AND provider='google'",
              (json.dumps(tokens), email))
    c.commit()
    c.close()
    return tokens["access_token"]


# ── Gmail lezen ────────────────────────────────────────────────────────────────

def fetch_messages(access_token: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Haal recente Gmail berichten op."""
    import base64

    headers = {"Authorization": f"Bearer {access_token}"}

    # Lijst ophalen
    resp = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers=headers,
        params={"maxResults": max_results, "labelIds": "INBOX"},
        timeout=15,
    )
    resp.raise_for_status()
    msg_ids = [m["id"] for m in resp.json().get("messages", [])]

    messages = []
    for msg_id in msg_ids[:max_results]:
        try:
            r = requests.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                headers=headers,
                params={"format": "metadata", "metadataHeaders": ["From", "Subject", "Date"]},
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            hdrs = {h["name"]: h["value"] for h in data.get("payload", {}).get("headers", [])}
            messages.append({
                "id": msg_id,
                "subject": hdrs.get("Subject", "(geen onderwerp)"),
                "from": hdrs.get("From", ""),
                "date": hdrs.get("Date", ""),
                "snippet": data.get("snippet", ""),
                "provider": "google",
            })
        except Exception:
            continue

    return messages


# ── Google Calendar ────────────────────────────────────────────────────────────

def fetch_calendar_events(access_token: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Haal komende agenda-items op uit Google Calendar."""
    from datetime import datetime, timezone

    headers = {"Authorization": f"Bearer {access_token}"}
    now = datetime.now(timezone.utc).isoformat()

    resp = requests.get(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers=headers,
        params={
            "maxResults": max_results,
            "orderBy": "startTime",
            "singleEvents": "true",
            "timeMin": now,
        },
        timeout=15,
    )
    resp.raise_for_status()

    events = []
    for item in resp.json().get("items", []):
        start = item.get("start", {})
        events.append({
            "id": item.get("id"),
            "title": item.get("summary", "(geen titel)"),
            "start": start.get("dateTime") or start.get("date", ""),
            "location": item.get("location", ""),
            "description": item.get("description", "")[:200],
            "provider": "google",
        })

    return events
