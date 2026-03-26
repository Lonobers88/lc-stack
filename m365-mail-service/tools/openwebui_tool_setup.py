"""
title: Redux Setup Assistent
author: Redux
version: 1.0.0
description: Beheerderstool voor het koppelen van Exact Online, Moneybird en M365 mailboxen. Alleen voor beheerders.
requirements: requests
"""

import os
from typing import Any, Dict, Optional
import requests


class Tools:
    def __init__(self):
        self.service_url = os.getenv("MAIL_SERVICE_URL", "http://m365-mail-service:8000")

    def _url(self, path: str) -> str:
        return f"{self.service_url}{path}"

    def check_all_connections(self) -> Dict[str, Any]:
        """
        Controleer de status van alle integraties: M365 mailboxen, Exact Online en Moneybird.

        Gebruik ALTIJD deze functie als eerste wanneer de beheerder het setup-scherm opent,
        of wanneer gevraagd wordt naar de status van koppelingen.

        :return: Overzicht van alle actieve en ontbrekende koppelingen.
        """
        status = {}

        # Mailboxen
        try:
            resp = requests.get(self._url("/mailboxes"), timeout=10)
            mailboxes = resp.json().get("mailboxes", [])
            status["mailboxen"] = {
                "gekoppeld": len(mailboxes) > 0,
                "aantal": len(mailboxes),
                "lijst": [f"{m.get('display_name', m.get('email'))} ({m.get('provider', 'm365')})" for m in mailboxes]
            }
        except Exception as e:
            status["mailboxen"] = {"gekoppeld": False, "fout": str(e)}

        # Exact Online
        try:
            resp = requests.get(self._url("/exact/invoices"), params={"max_results": 1}, timeout=10)
            if resp.status_code == 200:
                status["exact_online"] = {"gekoppeld": True, "status": "✅ Actief"}
            elif resp.status_code == 400 and "niet gekoppeld" in resp.text.lower():
                status["exact_online"] = {"gekoppeld": False, "status": "❌ Niet gekoppeld"}
            else:
                status["exact_online"] = {"gekoppeld": False, "status": f"⚠️ Fout: {resp.status_code}"}
        except Exception as e:
            status["exact_online"] = {"gekoppeld": False, "status": f"⚠️ {str(e)}"}

        # Moneybird
        try:
            resp = requests.get(self._url("/moneybird/invoices"), params={"max_results": 1}, timeout=10)
            if resp.status_code == 200:
                status["moneybird"] = {"gekoppeld": True, "status": "✅ Actief"}
            elif resp.status_code == 400 and "niet gekoppeld" in resp.text.lower():
                status["moneybird"] = {"gekoppeld": False, "status": "❌ Niet gekoppeld"}
            else:
                status["moneybird"] = {"gekoppeld": False, "status": f"⚠️ Fout: {resp.status_code}"}
        except Exception as e:
            status["moneybird"] = {"gekoppeld": False, "status": f"⚠️ {str(e)}"}

        return status

    def get_exact_setup_url(self, client_id: str) -> Dict[str, Any]:
        """
        Genereer de Exact Online autorisatie-URL voor de beheerder.

        Gebruik deze functie nadat de beheerder aangeeft dat ze Exact Online willen koppelen
        en hun Client ID hebben opgegeven.

        Stap 1 van de Exact koppeling:
        - Beheerder maakt app aan op apps.exactonline.com
        - Beheerder geeft Client ID op
        - Deze functie geeft de URL terug om te openen in de browser
        - Na inloggen bij Exact geeft de browser een 'pagina niet gevonden' — dat is normaal
        - De beheerder kopieert de code uit de URL-balk

        :param client_id: De Client ID van de Exact Online app (van apps.exactonline.com).
        :return: De URL om te openen in de browser, met instructies.
        """
        import urllib.parse
        params = urllib.parse.urlencode({
            "client_id": client_id,
            "redirect_uri": "http://localhost/callback",
            "response_type": "code",
            "force_login": "0",
        })
        auth_url = f"https://start.exactonline.nl/api/oauth2/auth?{params}"

        return {
            "stap": "1/2 — Open de URL in uw browser",
            "url": auth_url,
            "instructie": (
                f"**Open deze URL in uw browser:**\n{auth_url}\n\n"
                "Log in met uw Exact Online admin-account en geef toestemming. "
                "Daarna probeert de browser 'http://localhost/callback?code=XXXX' te laden — "
                "u ziet een foutpagina, dat is normaal. "
                "**Kopieer de volledige URL uit de adresbalk** en plak die hier terug."
            )
        }

    def complete_exact_setup(
        self,
        client_id: str,
        client_secret: str,
        callback_url: str,
        division: int,
    ) -> Dict[str, Any]:
        """
        Voltooi de Exact Online koppeling met de authorization code.

        Gebruik deze functie nadat de beheerder de callback URL heeft geplakt
        (de URL uit de browser-adresbalk na het inloggen bij Exact).

        Stap 2 van de Exact koppeling.

        :param client_id: De Client ID van de Exact Online app.
        :param client_secret: De Client Secret van de Exact Online app.
        :param callback_url: De volledige callback URL uit de browser (bijv. http://localhost/callback?code=XXXX).
        :param division: Het Exact Online divisienummer (staat in de URL als u ingelogd bent in Exact).
        :return: Status van de koppeling.
        """
        # Haal code uit de callback URL
        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(callback_url)
            params = parse_qs(parsed.query)
            code = params.get("code", [None])[0]
            if not code:
                # Misschien heeft de beheerder alleen de code geplakt
                code = callback_url.strip()
        except Exception:
            code = callback_url.strip()

        if not code:
            return {
                "status": "fout",
                "bericht": "Geen code gevonden in de opgegeven URL. Plak de volledige URL uit de adresbalk (bijv. http://localhost/callback?code=XXXX)."
            }

        try:
            resp = requests.post(self._url("/exact/connect"), json={
                "client_id": client_id,
                "client_secret": client_secret,
                "authorization_code": code,
                "division": division,
            }, timeout=20)

            if resp.status_code == 200:
                return {
                    "status": "✅ Exact Online succesvol gekoppeld!",
                    "divisie": division,
                    "bericht": "Exact Online is nu actief. Gebruikers met het Finance-model kunnen nu facturen, debiteuren en boekingen opvragen."
                }
            else:
                detail = resp.json().get("detail", resp.text)
                return {
                    "status": "❌ Koppeling mislukt",
                    "fout": detail,
                    "tip": "Controleer of Client ID, Client Secret en de code correct zijn. De code verloopt snel — probeer opnieuw als hij verlopen is."
                }
        except Exception as e:
            return {"status": "❌ Fout", "bericht": str(e)}

    def setup_moneybird(self, api_token: str) -> Dict[str, Any]:
        """
        Koppel Moneybird via een persoonlijk API token.

        Gebruik deze functie wanneer de beheerder Moneybird wil koppelen en een API token heeft.

        Hoe een Moneybird API token aanmaken:
        1. Log in op moneybird.com
        2. Ga naar Instellingen → Integraties → API
        3. Klik 'Nieuw token aanmaken'
        4. Kopieer het token en plak het hier

        :param api_token: Het persoonlijke Moneybird API token.
        :return: Status van de koppeling.
        """
        try:
            resp = requests.post(self._url("/moneybird/connect"), json={
                "api_token": api_token,
            }, timeout=20)

            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "✅ Moneybird succesvol gekoppeld!",
                    "administratie": data.get("administration"),
                    "administratie_id": data.get("administration_id"),
                    "bericht": "Moneybird is nu actief. Gebruikers met het Finance-model kunnen nu facturen en offertes opvragen."
                }
            else:
                detail = resp.json().get("detail", resp.text)
                return {
                    "status": "❌ Koppeling mislukt",
                    "fout": detail,
                    "tip": "Controleer of het API token correct is en voldoende rechten heeft."
                }
        except Exception as e:
            return {"status": "❌ Fout", "bericht": str(e)}

    def start_m365_mailbox_setup(self, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Start het koppelen van een Microsoft 365 mailbox via Device Code Flow.

        Gebruik wanneer de beheerder een M365 mailbox wil toevoegen.
        De beheerder krijgt een code en een URL te zien.

        :param email: Optioneel e-mailadres van de gebruiker.
        :return: Instructies met user_code en verificatie-URL.
        """
        try:
            resp = requests.post(self._url("/auth/device/start"), json={"email": email}, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            return {
                "stap": "Mailbox koppelen",
                "user_code": data.get("user_code"),
                "verificatie_url": data.get("verification_uri"),
                "device_code": data.get("device_code"),
                "instructie": (
                    f"**Open:** {data.get('verification_uri')}\n"
                    f"**Voer in:** `{data.get('user_code')}`\n\n"
                    f"Log in met het Microsoft 365-account dat u wilt koppelen. "
                    f"Zodra u klaar bent, zeg dan 'klaar' of 'gekoppeld'."
                ),
                "verloopt_over": f"{data.get('expires_in', 900) // 60} minuten"
            }
        except Exception as e:
            return {"status": "❌ Fout", "bericht": str(e)}

    def confirm_m365_mailbox(self, device_code: str) -> Dict[str, Any]:
        """
        Controleer of de M365 mailbox koppeling is afgerond.

        Gebruik nadat de beheerder aangeeft klaar te zijn met inloggen.

        :param device_code: De device_code van start_m365_mailbox_setup.
        :return: Status van de koppeling.
        """
        try:
            resp = requests.get(self._url("/auth/device/poll"),
                                params={"device_code": device_code}, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "connected":
                mailbox = data.get("mailbox", {})
                return {
                    "status": "✅ Mailbox succesvol gekoppeld!",
                    "email": mailbox.get("email"),
                    "naam": mailbox.get("display_name"),
                    "mailbox_id": mailbox.get("id"),
                    "bericht": f"De mailbox van {mailbox.get('display_name')} is actief. Gebruikers kunnen nu e-mails en agenda opvragen."
                }
            elif data.get("status") == "pending":
                return {
                    "status": "⏳ Nog niet afgerond",
                    "bericht": "De beheerder heeft nog niet ingelogd. Probeer opnieuw na het inloggen."
                }
            else:
                return data
        except Exception as e:
            return {"status": "❌ Fout", "bericht": str(e)}
