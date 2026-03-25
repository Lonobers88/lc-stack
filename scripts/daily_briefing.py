#!/usr/bin/env python3
"""
LC Dagelijkse Briefing - Cron script
Stuurt elke ochtend een gepersonaliseerde briefing naar elke OWUI gebruiker
met hun ongelezen mail + agenda voor vandaag.

Gebruik: python3 daily_briefing.py
Cron:    0 7 * * 1-5 /home/lc/lc-stack/scripts/daily_briefing.py

Environment variabelen (via .env of direct):
  OWUI_URL         = http://localhost:3000  (default)
  OWUI_ADMIN_TOKEN = <admin API token>
  MAIL_SERVICE_URL = http://localhost:8010  (default)
  BRIEFING_HOUR    = 7  (uur van de dag, default 7)
  BRIEFING_MODEL   = redux-medewerker  (model ID)
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

OWUI_URL = os.getenv("OWUI_URL", "http://localhost:3000")
OWUI_ADMIN_TOKEN = os.getenv("OWUI_ADMIN_TOKEN", "")
MAIL_SERVICE_URL = os.getenv("MAIL_SERVICE_URL", "http://localhost:8010")
BRIEFING_MODEL = os.getenv("BRIEFING_MODEL", "redux-medewerker")


def _http_get(url: str, token: str = "") -> Any:
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _http_post(url: str, data: dict, token: str = "") -> Any:
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def get_owui_users() -> List[Dict]:
    """Haal alle actieve OWUI gebruikers op."""
    try:
        data = _http_get(f"{OWUI_URL}/api/v1/users/", OWUI_ADMIN_TOKEN)
        return [u for u in data if u.get("role") in ("user", "admin")]
    except Exception as e:
        print(f"[ERROR] Gebruikers ophalen mislukt: {e}")
        return []


def get_mailboxes() -> List[Dict]:
    """Haal alle gekoppelde mailboxen op."""
    try:
        data = _http_get(f"{MAIL_SERVICE_URL}/mailboxes")
        return data.get("mailboxes", [])
    except Exception as e:
        print(f"[ERROR] Mailboxen ophalen mislukt: {e}")
        return []


def get_mail_for_mailbox(mailbox_id: int) -> List[Dict]:
    """Haal ongelezen mail op voor een mailbox."""
    try:
        data = _http_get(
            f"{MAIL_SERVICE_URL}/messages?mailbox_id={mailbox_id}&top=5&unread_only=true&folder=inbox"
        )
        return data.get("messages", [])
    except Exception as e:
        print(f"[WARN] Mail ophalen mislukt voor mailbox {mailbox_id}: {e}")
        return []


def get_calendar_for_mailbox(mailbox_id: int) -> List[Dict]:
    """Haal agenda van vandaag op voor een mailbox."""
    try:
        data = _http_get(
            f"{MAIL_SERVICE_URL}/calendar/events?mailbox_id={mailbox_id}&days_ahead=1&max_results=10"
        )
        return data.get("events", [])
    except Exception as e:
        print(f"[WARN] Agenda ophalen mislukt voor mailbox {mailbox_id}: {e}")
        return []


def build_briefing_prompt(user_email: str, mailboxes: List[Dict]) -> str:
    """Bouw de briefing context op voor een gebruiker."""
    today = datetime.now().strftime("%A %d %B %Y")
    parts = [f"[DAGELIJKSE BRIEFING - {today}]\n\nVoor: {user_email}\n"]

    # Mail per mailbox
    for mailbox in mailboxes:
        mid = mailbox.get("id")
        email = mailbox.get("email")
        msgs = get_mail_for_mailbox(mid)

        if msgs:
            mail_data = []
            for m in msgs:
                sender = m.get("from", {}).get("emailAddress", {})
                mail_data.append({
                    "mailbox": email,
                    "van_naam": sender.get("name", ""),
                    "van_email": sender.get("address", ""),
                    "onderwerp": m.get("subject", ""),
                    "datum": m.get("receivedDateTime", "")[:10],
                    "preview": m.get("bodyPreview", "")[:300],
                    "belang": m.get("importance", "normal"),
                })
            parts.append(f"\nONGELEZEN MAIL ({email}) - {len(msgs)} berichten:\n")
            parts.append(json.dumps(mail_data, ensure_ascii=False, indent=2))
        else:
            parts.append(f"\nONGELEZEN MAIL ({email}): Geen ongelezen berichten.\n")

    # Agenda per mailbox
    for mailbox in mailboxes:
        mid = mailbox.get("id")
        email = mailbox.get("email")
        events = get_calendar_for_mailbox(mid)

        if events:
            parts.append(f"\nAGENDA VANDAAG ({email}) - {len(events)} item(s):\n")
            for e in events:
                time_str = e.get("start", "")[-5:] if not e.get("is_all_day") else "Hele dag"
                parts.append(f"  {time_str} - {e.get('subject', '')} ({e.get('location', '')})")
        else:
            parts.append(f"\nAGENDA ({email}): Geen afspraken vandaag.")

    parts.append("""

INSTRUCTIE: Maak een korte, vriendelijke dagelijkse briefing in het Nederlands.
Geef:
1. Groet + datum
2. Samenvatting agenda (max 3-5 regels)
3. Prioritaire mail (top 3, kort gescoord op urgentie)
4. Aanbevolen actie voor vandaag (1 zin)

Houd het beknopt en to-the-point. Maximaal 200 woorden.""")

    return "\n".join(parts)


def send_chat_message(user_id: str, content: str) -> bool:
    """Stuur een bericht naar een OWUI gebruiker via de chat API."""
    try:
        # Maak een nieuwe chat aan
        chat = _http_post(
            f"{OWUI_URL}/api/v1/chats/new",
            {
                "chat": {
                    "title": f"Dagelijkse Briefing - {datetime.now().strftime('%d %b')}",
                    "models": [BRIEFING_MODEL],
                    "messages": [],
                }
            },
            OWUI_ADMIN_TOKEN,
        )
        chat_id = chat.get("id")
        if not chat_id:
            return False

        # Stuur het briefing verzoek
        _http_post(
            f"{OWUI_URL}/api/chat/completions",
            {
                "model": BRIEFING_MODEL,
                "messages": [
                    {"role": "user", "content": content}
                ],
                "stream": False,
            },
            OWUI_ADMIN_TOKEN,
        )
        return True
    except Exception as e:
        print(f"[WARN] Chat sturen mislukt voor {user_id}: {e}")
        return False


def main():
    print(f"[INFO] Dagelijkse briefing gestart - {datetime.now().isoformat()}")

    if not OWUI_ADMIN_TOKEN:
        print("[ERROR] OWUI_ADMIN_TOKEN niet ingesteld. Stel in via .env of environment.")
        sys.exit(1)

    mailboxes = get_mailboxes()
    if not mailboxes:
        print("[INFO] Geen mailboxen gekoppeld. Briefing overgeslagen.")
        return

    users = get_owui_users()
    print(f"[INFO] {len(users)} gebruikers, {len(mailboxes)} mailboxen gevonden")

    for user in users:
        user_email = user.get("email", "")
        user_id = user.get("id", "")

        # Koppel mailboxen aan gebruiker op basis van email domein
        # (simpel: gebruik alle mailboxen voor nu, later per-user koppeling)
        user_mailboxes = mailboxes

        prompt = build_briefing_prompt(user_email, user_mailboxes)
        success = send_chat_message(user_id, prompt)
        print(f"[{'OK' if success else 'FAIL'}] Briefing voor {user_email}")

    print(f"[INFO] Dagelijkse briefing klaar - {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
