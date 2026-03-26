"""
title: Redux M365 Mail, Agenda, Teams & Boekhouding
author: Redux
version: 0.3.0
description: Koppel M365/Google mailboxen, lees mail, agenda, Teams berichten, Exact Online en Moneybird facturen.
requirements: requests
"""

import os
from typing import Any, Dict, List, Optional

import requests


class Tools:
    def __init__(self):
        self.service_url = os.getenv("MAIL_SERVICE_URL", "http://m365-mail-service:8000")

    def _url(self, path: str) -> str:
        return f"{self.service_url}{path}"

    # ─── MAIL AUTH ───────────────────────────────────────────────────────────

    def start_device_login(self, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Start een Microsoft 365 Device Code Flow login. De gebruiker krijgt een code
        en een URL te zien om zich te authenticeren.

        Gebruik wanneer een gebruiker zijn/haar M365 mailbox wil koppelen.
        Geef de gebruiker de instructie: ga naar verification_uri en voer user_code in.

        :param email: Optioneel e-mailadres van de gebruiker (voor context).
        :return: JSON met user_code, verification_uri, message, expires_in en device_code.
        """
        payload = {"email": email}
        resp = requests.post(self._url("/auth/device/start"), json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return {
            "status": data.get("status"),
            "user_code": data.get("user_code"),
            "verification_uri": data.get("verification_uri"),
            "message": data.get("message"),
            "expires_in": data.get("expires_in"),
            "device_code": data.get("device_code"),
            "instructie": (
                f"Ga naar {data.get('verification_uri')} en voer code "
                f"**{data.get('user_code')}** in om je Microsoft-account te koppelen. "
                f"De code verloopt over {data.get('expires_in', 900) // 60} minuten."
            ),
        }

    def check_device_login(self, device_code: str) -> Dict[str, Any]:
        """
        Controleer of de gebruiker de Device Code Flow heeft afgerond.
        Roep aan nadat start_device_login is gebruikt en de gebruiker aangeeft klaar te zijn.

        :param device_code: De device_code van start_device_login.
        :return: JSON met status 'connected' of 'pending'/'error'.
        """
        resp = requests.get(
            self._url("/auth/device/poll"),
            params={"device_code": device_code},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "connected":
            mailbox = data.get("mailbox", {})
            return {
                "status": "connected",
                "mailbox_id": mailbox.get("id"),
                "email": mailbox.get("email"),
                "display_name": mailbox.get("display_name"),
                "bericht": f"✅ Mailbox van {mailbox.get('display_name')} ({mailbox.get('email')}) succesvol gekoppeld! Mailbox ID: {mailbox.get('id')}",
            }
        return data

    def list_mailboxes(self) -> Dict[str, Any]:
        """
        Toon alle gekoppelde mailboxen (M365, Google Workspace en IMAP).

        :return: JSON met gekoppelde mailboxen.
        """
        resp = requests.get(self._url("/mailboxes"), timeout=20)
        resp.raise_for_status()
        return resp.json()

    # ─── MAIL ────────────────────────────────────────────────────────────────

    def list_messages(
        self,
        mailbox_id: int,
        top: int = 10,
        folder: Optional[str] = None,
        unread_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Haal recente berichten op uit een gekoppelde mailbox.

        :param mailbox_id: ID van de gekoppelde mailbox.
        :param top: Aantal berichten om op te halen (max 50).
        :param folder: Optionele folder-naam of ID (bijv. 'inbox', 'sentitems').
        :param unread_only: Alleen ongelezen berichten ophalen.
        :return: JSON met berichten.
        """
        params = {"mailbox_id": mailbox_id, "top": top, "unread_only": unread_only}
        if folder:
            params["folder"] = folder
        resp = requests.get(self._url("/messages"), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def summarize_message(self, mailbox_id: int, message_id: str) -> Dict[str, Any]:
        """
        Haal berichtcontext, belangrijkheid en NL-samenvattingsprompt op voor één e-mail.

        :param mailbox_id: ID van de gekoppelde mailbox.
        :param message_id: Microsoft Graph message ID.
        :return: JSON met message, importance en summary_prompt_nl.
        """
        payload = {"mailbox_id": mailbox_id, "message_id": message_id}
        resp = requests.post(self._url("/summarize_message"), json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def draft_reply(
        self, mailbox_id: int, message_id: str, tone: str = "professioneel"
    ) -> Dict[str, Any]:
        """
        Genereer concept-antwoorden voor een e-mail. Verstuurt nooit mail.

        :param mailbox_id: ID van de gekoppelde mailbox.
        :param message_id: Microsoft Graph message ID.
        :param tone: Gewenste toon: professioneel, vriendelijk of direct.
        :return: JSON met draft_suggestions.
        """
        payload = {"mailbox_id": mailbox_id, "message_id": message_id, "tone": tone}
        resp = requests.post(self._url("/draft_reply"), json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()

    # ─── AGENDA ──────────────────────────────────────────────────────────────

    def get_calendar_events(
        self,
        mailbox_id: int,
        days_ahead: int = 1,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """
        Haal agenda-items op voor een specifieke mailbox.
        Werkt met zowel Microsoft 365 als Google Workspace mailboxen.

        Gebruik wanneer een gebruiker vraagt: "wat staat er op mijn agenda?",
        "welke meetings heb ik vandaag?" of "wat heb ik morgen?"

        :param mailbox_id: ID van de gekoppelde mailbox.
        :param days_ahead: Hoeveel dagen vooruit ophalen (1=vandaag, 2=morgen ook, etc.).
        :param max_results: Maximum aantal agenda-items (max 50).
        :return: JSON met events lijst.
        """
        params = {
            "mailbox_id": mailbox_id,
            "days_ahead": days_ahead,
            "max_results": max_results,
        }
        resp = requests.get(self._url("/calendar/events"), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def get_all_calendars(
        self,
        days_ahead: int = 1,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """
        Haal agenda-items op van ALLE gekoppelde mailboxen gecombineerd.
        Gesorteerd op starttijd. Handig voor een teamoverzicht.

        Gebruik wanneer een gebruiker vraagt: "wat staat er vandaag op de agenda?",
        "hebben we vandaag meetings?" of "geef me een dagplanning."

        :param days_ahead: Hoeveel dagen vooruit ophalen.
        :param max_results: Maximum per mailbox (max 50).
        :return: JSON met gecombineerde events van alle mailboxen.
        """
        params = {"days_ahead": days_ahead, "max_results": max_results}
        resp = requests.get(self._url("/calendar/all"), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    # ─── TEAMS ───────────────────────────────────────────────────────────────

    def get_teams_messages(
        self,
        mailbox_id: int,
        hours_back: int = 24,
    ) -> Dict[str, Any]:
        """
        Haal recente Microsoft Teams berichten op voor een M365 mailbox.
        Geeft een overzicht van berichten per channel uit de afgelopen X uur.

        Gebruik wanneer een gebruiker vraagt: "wat is er in Teams besproken?",
        "zijn er nieuwe Teams berichten?" of "vat Teams samen."

        :param mailbox_id: ID van de M365 mailbox (Teams werkt alleen met M365).
        :param hours_back: Hoeveel uur terug kijken (max 168 = 1 week).
        :return: JSON met teams_messages per channel.
        """
        params = {"mailbox_id": mailbox_id, "hours_back": hours_back}
        resp = requests.get(self._url("/teams/messages"), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ─── EXACT ONLINE ────────────────────────────────────────────────────────

    def get_exact_invoices(self, max_results: int = 10) -> Dict[str, Any]:
        """
        Haal openstaande verkoopfacturen op uit Exact Online.

        Gebruik wanneer een gebruiker vraagt: "welke facturen staan nog open?",
        "wat zijn mijn openstaande facturen?" of "hoeveel moet ik nog ontvangen?"

        Vereist dat Exact Online eenmalig is gekoppeld via de beheerder.
        Als de koppeling ontbreekt, geef dan instructie om contact op te nemen met de beheerder.

        :param max_results: Maximum aantal facturen (max 50).
        :return: JSON met openstaande facturen.
        """
        params = {"max_results": max_results}
        resp = requests.get(self._url("/exact/invoices"), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def get_exact_receivables(self, max_results: int = 10) -> Dict[str, Any]:
        """
        Haal openstaande debiteuren op uit Exact Online.

        Gebruik wanneer een gebruiker vraagt: "wie moet ik nog betalen?",
        "welke klanten hebben nog een openstaand bedrag?" of "debiteurenoverzicht."

        :param max_results: Maximum aantal debiteuren (max 50).
        :return: JSON met openstaande debiteuren.
        """
        params = {"max_results": max_results}
        resp = requests.get(self._url("/exact/receivables"), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def get_exact_transactions(self, max_results: int = 10) -> Dict[str, Any]:
        """
        Haal recente boekingen op uit Exact Online.

        Gebruik wanneer een gebruiker vraagt: "wat zijn de laatste boekingen?",
        "toon recente transacties" of "wat is er onlangs geboekt?"

        :param max_results: Maximum aantal boekingen (max 50).
        :return: JSON met recente transacties.
        """
        params = {"max_results": max_results}
        resp = requests.get(self._url("/exact/transactions"), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    # ─── MONEYBIRD ───────────────────────────────────────────────────────────

    def get_moneybird_invoices(self, max_results: int = 10) -> Dict[str, Any]:
        """
        Haal onbetaalde facturen op uit Moneybird.

        Gebruik wanneer een gebruiker vraagt: "welke Moneybird facturen staan open?",
        "hoeveel moet ik nog ontvangen?" of "toon onbetaalde facturen."

        Vereist dat Moneybird eenmalig is gekoppeld via de beheerder.

        :param max_results: Maximum aantal facturen (max 50).
        :return: JSON met onbetaalde facturen uit Moneybird.
        """
        params = {"max_results": max_results}
        resp = requests.get(self._url("/moneybird/invoices"), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def get_moneybird_estimates(self, max_results: int = 5) -> Dict[str, Any]:
        """
        Haal recente offertes op uit Moneybird.

        Gebruik wanneer een gebruiker vraagt: "welke offertes zijn er uitgestuurd?",
        "toon recente offertes" of "wat staat er nog open aan offertes?"

        :param max_results: Maximum aantal offertes (max 20).
        :return: JSON met recente offertes uit Moneybird.
        """
        params = {"max_results": max_results}
        resp = requests.get(self._url("/moneybird/estimates"), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()
