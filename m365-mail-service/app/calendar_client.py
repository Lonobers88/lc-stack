"""
Agenda client voor lc-mail-service.
Ondersteunt M365 Calendar (Graph API) en Google Calendar (service account).
Output formaat is unified zodat de pipe beide providers gelijk behandelt.
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional


# ─── M365 Calendar ────────────────────────────────────────────────────────────

def fetch_m365_events(
    mailbox: Dict[str, Any],
    days_ahead: int = 1,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Haal agenda-items op via Microsoft Graph Calendar API."""
    from .graph import get_access_token, graph_get

    access_token = get_access_token(mailbox)

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days_ahead)

    params = {
        "$select": "id,subject,start,end,location,organizer,isAllDay,bodyPreview,isCancelled",
        "$orderby": "start/dateTime",
        "$top": max_results,
        "startDateTime": now.isoformat(),
        "endDateTime": end.isoformat(),
    }

    data = graph_get(access_token, "/me/calendarView", params=params)
    events = data.get("value", [])

    return [_normalize_m365_event(e) for e in events]


def _normalize_m365_event(e: Dict[str, Any]) -> Dict[str, Any]:
    start = e.get("start", {})
    end = e.get("end", {})
    organizer = e.get("organizer", {}).get("emailAddress", {})
    location = e.get("location", {}).get("displayName", "")

    return {
        "id": e.get("id", "")[:40],
        "subject": e.get("subject", "(geen onderwerp)"),
        "start": start.get("dateTime", "")[:16].replace("T", " "),
        "end": end.get("dateTime", "")[:16].replace("T", " "),
        "is_all_day": e.get("isAllDay", False),
        "location": location,
        "organizer_name": organizer.get("name", ""),
        "organizer_email": organizer.get("address", ""),
        "preview": e.get("bodyPreview", "")[:200],
        "cancelled": e.get("isCancelled", False),
    }


# ─── Google Calendar ──────────────────────────────────────────────────────────

def fetch_google_events(
    mailbox: Dict[str, Any],
    days_ahead: int = 1,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Haal agenda-items op via Google Calendar API met service account."""
    from googleapiclient.discovery import build
    from google.oauth2 import service_account

    service_account_json = mailbox.get("imap_config")
    if not service_account_json:
        raise ValueError("Google service account niet geconfigureerd")

    info = json.loads(service_account_json)
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/calendar.readonly",
    ]
    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES
    ).with_subject(mailbox["email"])

    service = build("calendar", "v3", credentials=credentials, cache_discovery=False)

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days_ahead)

    result = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = result.get("items", [])
    return [_normalize_google_event(e) for e in events]


def _normalize_google_event(e: Dict[str, Any]) -> Dict[str, Any]:
    start = e.get("start", {})
    end = e.get("end", {})
    organizer = e.get("organizer", {})

    # All-day events hebben 'date', timed events hebben 'dateTime'
    start_str = start.get("dateTime", start.get("date", ""))[:16].replace("T", " ")
    end_str = end.get("dateTime", end.get("date", ""))[:16].replace("T", " ")
    is_all_day = "date" in start and "dateTime" not in start

    return {
        "id": e.get("id", "")[:40],
        "subject": e.get("summary", "(geen onderwerp)"),
        "start": start_str,
        "end": end_str,
        "is_all_day": is_all_day,
        "location": e.get("location", ""),
        "organizer_name": organizer.get("displayName", ""),
        "organizer_email": organizer.get("email", ""),
        "preview": e.get("description", "")[:200],
        "cancelled": e.get("status") == "cancelled",
    }


# ─── Unified fetch ─────────────────────────────────────────────────────────────

def fetch_events(
    mailbox: Dict[str, Any],
    days_ahead: int = 1,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Haal agenda-items op voor een mailbox, ongeacht provider."""
    provider = mailbox.get("provider", "m365")

    if provider == "google":
        return fetch_google_events(mailbox, days_ahead=days_ahead, max_results=max_results)
    else:
        # m365 (en als fallback alles anders)
        return fetch_m365_events(mailbox, days_ahead=days_ahead, max_results=max_results)
