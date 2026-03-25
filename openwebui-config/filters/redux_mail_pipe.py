"""
title: LC Mail Pipe
description: Detecteert mail-intentie en roept de LC mail service aan. Ondersteunt M365 en IMAP.
author: LocalCompute
version: 2.0
required_open_webui_version: 0.3.0
"""

import json
import re
import urllib.request
import urllib.error
from typing import Optional
from pydantic import BaseModel, Field

MAIL_SERVICE_URL = "http://m365-mail-service:8000"

INTENT_KOPPEL_M365 = ["koppel microsoft", "verbind microsoft", "koppel m365", "m365 koppelen", "microsoft 365 koppelen", "outlook koppelen", "login microsoft", "microsoft account koppelen"]
INTENT_KOPPEL_IMAP = ["koppel imap", "imap koppelen", "koppel gmail", "gmail koppelen", "koppel mijn email", "imap instellen", "email server koppelen", "koppel mailserver"]
INTENT_KOPPEL_ANY = ["koppel", "verbind", "connect", "mailbox toevoegen", "account koppelen", "mail koppelen"]
INTENT_IMAP_DATA = ["imap_host:", "host:", "wachtwoord:", "password:", "gebruikersnaam:", "username:"]
INTENT_INBOX = [
    "inbox", "mailbox", "mijn mail", "mn mail", "nieuwe mail", "mails",
    "check mail", "check mijn", "check mn", "mail checken", "mail nakijken", "mail controleren",
    "mail lezen", "e-mails", "e-mail", "berichten bekijken", "mail tonen", "emails tonen",
    "mailbox zien", "mails zien", "toon mijn", "laat mijn", "bekijk mijn", "open mijn mail",
    "heb ik mail", "zijn er mails", "nieuwe berichten", "ongelezen", "ongelezen berichten",
    "post", "berichtenbox",
    # Engels
    "check my", "my inbox", "my mail", "my email", "my mailbox",
    "read mail", "show mail", "get mail", "any mail", "new mail", "unread",
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
    import re as _re
    t = _re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "", text.lower())
    # IMAP data ingevoerd (tweede stap van IMAP koppelen)
    if any(kw in t for kw in INTENT_IMAP_DATA):
        return "imap_data"
    # Specifiek M365
    if any(kw in t for kw in INTENT_KOPPEL_M365):
        return "koppel_m365"
    # Specifiek IMAP/Gmail
    if any(kw in t for kw in INTENT_KOPPEL_IMAP):
        return "koppel_imap_start"
    # Generiek koppelen (M365 als default)
    if any(kw in t for kw in INTENT_KOPPEL_ANY):
        return "koppel_m365"
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


def _is_awaiting_imap(messages: list) -> bool:
    """Kijk of de AI in de vorige berichten om IMAP gegevens heeft gevraagd."""
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            content = (msg.get("content", "") or "").lower()
            if "imap" in content and ("host" in content or "wachtwoord" in content or "server" in content):
                return True
            break
    return False


def _parse_imap_data(text: str) -> Optional[dict]:
    """Probeer IMAP gegevens te parsen uit vrije tekst."""
    result = {}
    lines = text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip().lower().replace(" ", "_")
            val = val.strip()
            if key in ("email", "e-mail"):
                result["email"] = val
            elif key in ("imap_host", "host", "server", "imap_server"):
                result["imap_host"] = val
            elif key in ("imap_port", "port", "poort"):
                try:
                    result["imap_port"] = int(val)
                except ValueError:
                    pass
            elif key in ("username", "gebruikersnaam", "gebruiker"):
                result["username"] = val
            elif key in ("password", "wachtwoord", "app_wachtwoord", "app_password"):
                result["password"] = val
            elif key in ("ssl", "imap_ssl"):
                result["imap_ssl"] = val.lower() not in ("false", "nee", "no", "0")
            elif key in ("naam", "name", "display_name"):
                result["display_name"] = val

    required = {"email", "imap_host", "username", "password"}
    if required.issubset(result.keys()):
        return result
    return None


class Pipe:
    class Valves(BaseModel):
        mail_service_url: str = Field(
            default="http://m365-mail-service:8000",
            description="URL van de mail service"
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
        self.name = "LC Mail Pipe"

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

        # Als de AI om IMAP gegevens heeft gevraagd en de user nu data stuurt
        if intent == "none" and _is_awaiting_imap(messages):
            parsed = _parse_imap_data(last_user_msg)
            if parsed:
                intent = "imap_data"

        service_url = self.valves.mail_service_url
        injection = None

        if intent == "koppel_m365":
            result = _http("POST", f"{service_url}/auth/device/start", data={})
            if "error" in result:
                injection = f"[MAIL SERVICE FOUT]: {result['error']}"
            else:
                user_code = result.get("user_code", "?")
                verification_uri = result.get("verification_uri", "https://login.microsoft.com/device")
                expires_in = result.get("expires_in", 900)
                device_code = result.get("device_code", "")
                injection = (
                    f"[MAIL KOPPELEN - M365 DEVICE CODE FLOW GESTART]\n"
                    f"user_code: {user_code}\n"
                    f"verification_uri: {verification_uri}\n"
                    f"expires_in: {expires_in}\n"
                    f"device_code: {device_code}\n\n"
                    f"Instructie voor de assistent: Vertel de gebruiker dat ze naar {verification_uri} "
                    f"moeten gaan en code **{user_code}** moeten invoeren. "
                    f"De code verloopt over {expires_in // 60} minuten. "
                    f"Sla de device_code op voor later gebruik."
                )

        elif intent == "koppel_imap_start":
            injection = (
                "[IMAP KOPPELEN - GEGEVENS NODIG]\n\n"
                "Instructie voor de assistent: Vraag de gebruiker om de volgende IMAP gegevens in te voeren. "
                "Leg uit dat ze dit in één bericht kunnen sturen in dit formaat:\n\n"
                "email: jan@bedrijf.nl\n"
                "imap_host: mail.bedrijf.nl\n"
                "imap_port: 993\n"
                "ssl: ja\n"
                "gebruikersnaam: jan@bedrijf.nl\n"
                "wachtwoord: [app-wachtwoord]\n\n"
                "Tip: Voor Gmail gebruik imap.gmail.com poort 993. "
                "Zorg dat 'toegang voor minder veilige apps' of een App Password is ingesteld. "
                "Voor Outlook/Hotmail: outlook.office365.com poort 993."
            )

        elif intent == "imap_data":
            parsed = _parse_imap_data(last_user_msg)
            if not parsed:
                injection = (
                    "[IMAP GEGEVENS ONVOLLEDIG]\n"
                    "Instructie: De gebruiker heeft onvolledige IMAP gegevens gestuurd. "
                    "Vraag opnieuw om: email, imap_host, gebruikersnaam en wachtwoord. "
                    "imap_port en ssl zijn optioneel (standaard: 993, ssl=ja)."
                )
            else:
                payload = {
                    "email": parsed["email"],
                    "display_name": parsed.get("display_name"),
                    "imap_host": parsed["imap_host"],
                    "imap_port": parsed.get("imap_port", 993),
                    "imap_ssl": parsed.get("imap_ssl", True),
                    "username": parsed["username"],
                    "password": parsed["password"],
                }
                result = _http("POST", f"{service_url}/imap/connect", data=payload)
                if "error" in result:
                    injection = (
                        f"[IMAP VERBINDING MISLUKT]\n"
                        f"Fout: {result['error']}\n\n"
                        f"Instructie: Vertel de gebruiker dat de verbinding mislukt is. "
                        f"Vraag of de gegevens kloppen (host, gebruikersnaam, wachtwoord). "
                        f"Bij Gmail: controleer of een App Password is gebruikt."
                    )
                else:
                    mailbox = result.get("mailbox", {})
                    injection = (
                        f"[IMAP MAILBOX SUCCESVOL GEKOPPELD]\n"
                        f"email: {mailbox.get('email')}\n"
                        f"naam: {mailbox.get('display_name')}\n"
                        f"provider: IMAP\n"
                        f"mailbox_id: {mailbox.get('id')}\n\n"
                        f"Instructie: Feliciteer de gebruiker. De IMAP mailbox is nu beschikbaar. "
                        f"Ze kunnen nu 'check mijn mail' gebruiken om berichten op te halen."
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
                        "Er zijn nog geen mailboxen gekoppeld. "
                        "Vraag de gebruiker of ze Microsoft 365 of IMAP mail willen koppelen."
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
                "content": "## Mail Service Resultaat\n\n" + injection
            }
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    messages.insert(i, inject_msg)
                    break
            body["messages"] = messages

        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        return body
