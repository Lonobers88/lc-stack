"""
title: Redux M365 Mail Pipe
description: Detecteert mail-intentie en roept de M365 service direct aan. Geen tool-calling nodig.
author: Redux Gaming
version: 1.1
required_open_webui_version: 0.3.0
"""

import json
import re
import urllib.request
import urllib.error
from typing import Optional
from pydantic import BaseModel, Field

MAIL_SERVICE_URL = "http://m365-mail-service:8000"

INTENT_KOPPEL = ["koppel", "verbind", "connect", "login microsoft", "mailbox toevoegen", "account koppelen", "m365 koppelen", "mail koppelen"]
INTENT_INBOX = [
    # Directe inbox-verzoeken
    "inbox", "mailbox", "mijn mail", "mn mail", "nieuwe mail", "mails",
    # Check-varianten
    "check mail", "check mijn", "check mn", "mail checken", "mail nakijken", "mail controleren",
    # Lees/bekijk-varianten
    "mail lezen", "e-mails", "e-mail", "berichten bekijken", "mail tonen", "emails tonen",
    "mailbox zien", "mails zien", "toon mijn", "laat mijn", "bekijk mijn", "open mijn mail",
    # Vraagvarianten
    "heb ik mail", "zijn er mails", "nieuwe berichten", "ongelezen", "ongelezen berichten",
    # Overig
    "post", "berichtenbox",
]
INTENT_POLL = ["klaar", "ingelogd", "gedaan", "afgerond", "ik heb de code ingevoerd", "gelukt", "verbonden"]


def _http(method: str, url: str, data: Optional[dict] = None, params: Optional[dict] = None) -> dict:
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def _detect_intent(text: str) -> str:
    t = text.lower()
    if any(kw in t for kw in INTENT_KOPPEL):
        return "koppel"
    if any(kw in t for kw in INTENT_POLL):
        return "poll"
    if any(kw in t for kw in INTENT_INBOX):
        return "inbox"
    return "none"


def _extract_device_code(messages: list) -> Optional[str]:
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            match = re.search(r'"device_code":\s*"([^"]{20,})"', content)
            if match:
                return match.group(1)
            match = re.search(r'device_code[:\s]+([A-Za-z0-9_\-]{20,})', content)
            if match:
                return match.group(1)
    return None


class Pipe:
    class Valves(BaseModel):
        mail_service_url: str = Field(
            default="http://m365-mail-service:8000",
            description="URL van de M365 mail service"
        )
        max_messages: int = Field(
            default=10,
            description="Aantal e-mails om op te halen bij inbox-verzoek"
        )
        enabled: bool = Field(
            default=True,
            description="Schakel de mail pipe in/uit"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.type = "filter"
        self.name = "Redux M365 Mail"

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        if not self.valves.enabled:
            return body

        messages = body.get("messages", [])
        if not messages:
            return body

        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                last_user_msg = content if isinstance(content, str) else str(content)
                break

        if not last_user_msg.strip():
            return body

        intent = _detect_intent(last_user_msg)
        service_url = self.valves.mail_service_url
        injection = None

        if intent == "koppel":
            result = _http("POST", f"{service_url}/auth/device/start", data={})
            if "error" in result:
                injection = f"[MAIL SERVICE FOUT]: {result['error']}"
            else:
                user_code = result.get("user_code", "?")
                verification_uri = result.get("verification_uri", "https://login.microsoft.com/device")
                expires_in = result.get("expires_in", 900)
                device_code = result.get("device_code", "")
                injection = (
                    f"[MAIL KOPPELEN - DEVICE CODE FLOW GESTART]\n"
                    f"user_code: {user_code}\n"
                    f"verification_uri: {verification_uri}\n"
                    f"expires_in: {expires_in}\n"
                    f"device_code: {device_code}\n\n"
                    f"Instructie voor de assistent: Vertel de gebruiker dat ze naar {verification_uri} "
                    f"moeten gaan en code **{user_code}** moeten invoeren. "
                    f"De code verloopt over {expires_in // 60} minuten. "
                    f"Sla de device_code op voor later gebruik."
                )

        elif intent == "poll":
            device_code = _extract_device_code(messages)
            params = {"device_code": device_code} if device_code else {}
            result = _http("GET", f"{service_url}/auth/device/poll", params=params)
            if "error" in result:
                injection = f"[MAIL POLL FOUT]: {result['error']}"
            elif result.get("status") == "connected":
                mailbox = result.get("mailbox", {})
                injection = (
                    f"[MAILBOX SUCCESVOL GEKOPPELD]\n"
                    f"email: {mailbox.get('email')}\n"
                    f"naam: {mailbox.get('display_name')}\n"
                    f"mailbox_id: {mailbox.get('id')}\n\n"
                    f"Instructie: Feliciteer de gebruiker. Mailbox is nu beschikbaar."
                )
            elif result.get("status") == "pending":
                injection = (
                    "[MAIL STATUS: WACHT NOG]\n"
                    "De gebruiker heeft nog niet ingelogd. "
                    "Vertel dat ze de code nog moeten invoeren op de Microsoft pagina."
                )
            else:
                injection = f"[MAIL STATUS]: {json.dumps(result)}"

        elif intent == "inbox":
            mailboxes = _http("GET", f"{service_url}/mailboxes")
            if "error" in mailboxes:
                injection = (
                    f"[MAIL FOUT]: {mailboxes['error']}\n"
                    "Vraag de gebruiker of ze hun mailbox al hebben gekoppeld."
                )
            else:
                boxes = mailboxes.get("mailboxes", [])
                if not boxes:
                    injection = (
                        "[GEEN MAILBOXEN GEKOPPELD]\n"
                        "Er zijn nog geen Microsoft 365 mailboxen gekoppeld. "
                        "Vraag de gebruiker of ze hun mailbox willen koppelen."
                    )
                else:
                    mailbox = boxes[0]
                    mid = mailbox.get("id")
                    messages_result = _http(
                        "GET", f"{service_url}/messages",
                        params={"mailbox_id": mid, "top": self.valves.max_messages, "unread_only": "true", "folder": "inbox"}
                    )
                    if "error" in messages_result:
                        injection = f"[MAIL FOUT bij ophalen berichten]: {messages_result['error']}"
                    else:
                        msgs = messages_result.get("messages", [])
                        if not msgs:
                            injection = f"[INBOX VAN {mailbox.get('email')}]: Geen ongelezen berichten. Je inbox is bij!"
                        else:
                            # Geef ruwe maildata door — LLM past het scoring-format toe
                            mail_data = []
                            for m in msgs:
                                sender = m.get("from", {}).get("emailAddress", {})
                                mail_data.append({
                                    "van_naam": sender.get("name", ""),
                                    "van_email": sender.get("address", ""),
                                    "onderwerp": m.get("subject", "(geen onderwerp)"),
                                    "datum": m.get("receivedDateTime", "")[:10],
                                    "ongelezen": m.get("isRead") is False,
                                    "belang": m.get("importance", "normal"),
                                    "preview": m.get("bodyPreview", "")[:400],
                                    "id": m.get("id", "")[:40],
                                })
                            mail_json = json.dumps(mail_data, ensure_ascii=False, indent=2)
                            injection = (
                                f"[INBOX VAN {mailbox.get('email')} - {len(msgs)} BERICHTEN]\n\n"
                                f"RUWE MAILDATA:\n{mail_json}\n\n"
                                f"INSTRUCTIE: Verwerk bovenstaande e-mails VOLLEDIG volgens het mail scoring format "
                                f"uit je system prompt. Geef per mail:\n"
                                f"- Urgentiescore 1-10 en relevantiescorenatiescore 1-10 met uitleg\n"
                                f"- Volledige samenvatting (geen lengte limiet)\n"
                                f"- Volledig concept-reply bij urgentie >= 6 en actie vereist\n"
                                f"Sorteer op urgentie, hoogste eerst. Taal: Nederlands."
                            )

        if injection:
            inject_msg = {
                "role": "system",
                "content": "## M365 Mail Service Resultaat\n\n" + injection
            }
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    messages.insert(i, inject_msg)
                    break
            body["messages"] = messages

        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        return body
