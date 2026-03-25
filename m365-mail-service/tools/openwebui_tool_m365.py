"""
title: Redux M365 Mail
author: Redux
version: 0.2.0
description: Koppel Microsoft 365 mailboxen via Device Code Flow en haal mailbox-overzichten, samenvattingen, belangrijkheid en concept-antwoorden op.
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

    def start_device_login(self, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Start een Microsoft 365 Device Code Flow login. De gebruiker krijgt een code
        en een URL te zien om zich te authenticeren.

        Gebruik deze functie wanneer een gebruiker zijn/haar M365 mailbox wil koppelen.
        Geef de gebruiker de instructie: ga naar verification_uri en voer user_code in.
        Sla daarna device_code op voor gebruik in check_device_login.

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
        Roep deze functie aan nadat start_device_login is gebruikt en de gebruiker
        aangeeft dat hij/zij klaar is met inloggen.

        :param device_code: De device_code die je kreeg van start_device_login.
        :return: JSON met status 'connected' (met mailbox info) of 'pending'/'error'.
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
        Toon alle gekoppelde mailboxen.

        :return: JSON met gekoppelde mailboxen.
        """
        resp = requests.get(self._url("/mailboxes"), timeout=20)
        resp.raise_for_status()
        return resp.json()

    def list_messages(self, mailbox_id: int, top: int = 10, folder: Optional[str] = None) -> Dict[str, Any]:
        """
        Haal recente berichten op uit een gekoppelde mailbox.

        :param mailbox_id: ID van de gekoppelde mailbox.
        :param top: Aantal berichten om op te halen.
        :param folder: Optionele Microsoft 365 folder-id of bekende foldernaam.
        :return: JSON met berichten.
        """
        params = {"mailbox_id": mailbox_id, "top": top}
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

    def draft_reply(self, mailbox_id: int, message_id: str, tone: str = "professioneel") -> Dict[str, Any]:
        """
        Genereer concept-antwoorden voor een e-mail. Deze tool verstuurt nooit mail.

        :param mailbox_id: ID van de gekoppelde mailbox.
        :param message_id: Microsoft Graph message ID.
        :param tone: Gewenste toon, bijvoorbeeld professioneel, vriendelijk of direct.
        :return: JSON met draft_suggestions.
        """
        payload = {"mailbox_id": mailbox_id, "message_id": message_id, "tone": tone}
        resp = requests.post(self._url("/draft_reply"), json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()
