"""
Exact Online client voor lc-mail-service.
Gebruikt admin API key (client credentials / refresh token) — geen redirect OAuth nodig.

Setup door admin:
1. Maak een Exact Online App aan op apps.exactonline.com
2. Gebruik Client Credentials flow of sla een long-lived refresh token op
3. Sla op in .env: EXACT_CLIENT_ID, EXACT_CLIENT_SECRET, EXACT_REFRESH_TOKEN, EXACT_DIVISION

Exact Online gebruikt OAuth2 met refresh tokens die lang geldig zijn.
De admin koppelt eenmalig via de tool; daarna werkt het automatisch.
"""

import json
import re
import os
import time
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Any, Dict, List, Optional


EXACT_TOKEN_URL = "https://start.exactonline.nl/api/oauth2/token"
EXACT_API_BASE = "https://start.exactonline.nl/api/v1"


class ExactTokenStore:
    """Beheert access/refresh tokens voor Exact Online."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exact_tokens (
                id INTEGER PRIMARY KEY,
                client_id TEXT,
                client_secret TEXT,
                access_token TEXT,
                refresh_token TEXT,
                division INTEGER,
                expires_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def save(self, client_id: str, client_secret: str, access_token: str,
             refresh_token: str, division: int, expires_in: int):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM exact_tokens WHERE id = 1")
        conn.execute(
            "INSERT INTO exact_tokens VALUES (1, ?, ?, ?, ?, ?, ?)",
            (client_id, client_secret, access_token, refresh_token,
             division, time.time() + expires_in - 60)
        )
        conn.commit()
        conn.close()

    def load(self) -> Optional[Dict]:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM exact_tokens WHERE id = 1").fetchone()
        conn.close()
        return dict(row) if row else None


def _get_token_store(db_path: str) -> ExactTokenStore:
    return ExactTokenStore(db_path)


def _refresh_access_token(store: ExactTokenStore, config: Dict) -> str:
    """Vernieuw access token via refresh token."""
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": config["refresh_token"],
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
    }).encode()

    req = urllib.request.Request(EXACT_TOKEN_URL, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        raise ValueError(f"Exact Online refresh token verlopen of ongeldig. Koppeling opnieuw vereist. Fout: {e}")

    if not isinstance(result, dict) or "access_token" not in result:
        raise ValueError(f"Exact Online onverwachte response bij token refresh: {str(result)[:200]}")

    store.save(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        access_token=result["access_token"],
        refresh_token=result.get("refresh_token", config["refresh_token"]),
        division=config["division"],
        expires_in=int(result.get("expires_in", 600)),
    )
    return result["access_token"]


def _get_access_token(db_path: str) -> tuple:
    """Geeft (access_token, division) terug, vernieuwt indien verlopen."""
    store = _get_token_store(db_path)
    config = store.load()
    if not config:
        raise ValueError("Exact Online niet gekoppeld. Gebruik POST /exact/connect eerst.")

    if time.time() > config["expires_at"]:
        token = _refresh_access_token(store, config)
    else:
        token = config["access_token"]

    return token, config["division"]


def _exact_get(token: str, division: int, endpoint: str, params: Optional[Dict] = None) -> Dict:
    """Voer een GET request uit op de Exact Online API."""
    url = f"{EXACT_API_BASE}/{division}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def connect_exact(client_id: str, client_secret: str, authorization_code: str,
                  division: int, db_path: str) -> Dict:
    """
    Koppel Exact Online via authorization code (eenmalig door admin).
    De admin genereert de authorization code via de Exact Online App.
    """
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "https://callback.localcompute.nl/",
    }).encode()

    req = urllib.request.Request(EXACT_TOKEN_URL, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        raise ValueError(f"Exact Online koppeling mislukt: {str(e)}")

    store = _get_token_store(db_path)
    store.save(
        client_id=client_id,
        client_secret=client_secret,
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        division=division,
        expires_in=int(result.get("expires_in", 600)),
    )
    return {"status": "connected", "division": division}


def _format_exact_date(value: Any) -> str:
    if value is None:
        return ""
    value = str(value)
    if "/Date(" in value:
        match = re.search(r"\d+", value)
        if match:
            return str(datetime.fromtimestamp(int(match.group()) // 1000).date())
    return value[:10]


def _lookup_account_names(token: str, division: str, guids: list) -> dict:
    """Directe lookup van account namen via GUIDs. Retourneert {guid: naam} dict."""
    if not guids:
        return {}
    result = {}
    for guid in guids[:15]:  # max 15 lookups
        try:
            data = _exact_get(token, division, f"crm/Accounts(guid'{guid}')", params={
                "$select": "ID,Name",
            })
            d = data.get("d", {})
            name = d.get("Name", "")
            if name:
                result[guid.lower()] = name
        except Exception:
            continue
    return result


def get_open_invoices(db_path: str, max_results: int = 10) -> List[Dict]:
    """Haal openstaande verkoopfacturen op."""
    token, division = _get_access_token(db_path)

    data = _exact_get(token, division, "salesinvoice/SalesInvoices", params={
        "$top": max_results,
        "$orderby": "InvoiceDate desc",
    })

    if not isinstance(data, dict):
        raise ValueError(f"Exact Online API onverwachte response: {str(data)[:200]}")
    invoices = (lambda d: d if isinstance(d, list) else d.get("results", []))(data.get("d", []))

    # Verzamel GUIDs voor facturen zonder klantnaam
    guid_set = set()
    for inv in invoices:
        name = inv.get("OrderedByName") or inv.get("InvoiceToName") or inv.get("DeliverToName")
        if not name:
            guid = inv.get("OrderedBy") or inv.get("InvoiceTo") or inv.get("DeliverTo")
            if guid and len(guid) == 36:  # is een GUID
                guid_set.add(guid.lower())

    # Batch-lookup voor ontbrekende namen
    account_map = _lookup_account_names(token, division, list(guid_set)) if guid_set else {}

    result = []
    for inv in invoices:
        name = inv.get("OrderedByName") or inv.get("InvoiceToName") or inv.get("DeliverToName")
        if not name:
            guid = (inv.get("OrderedBy") or inv.get("InvoiceTo") or inv.get("DeliverTo") or "").lower()
            name = account_map.get(guid, guid)  # fallback naar guid als naam onbekend
        result.append({
            "nummer": inv.get("InvoiceNumber") or inv.get("EntryNumber") or inv.get("YourRef"),
            "datum": _format_exact_date(inv.get("InvoiceDate", "")),
            "bedrag": inv.get("AmountDC"),
            "omschrijving": inv.get("Description", ""),
            "klant": name,
            "referentie": inv.get("YourRef", ""),
        })
    return result


def get_open_receivables(db_path: str, max_results: int = 10) -> List[Dict]:
    """Haal openstaande debiteuren op."""
    token, division = _get_access_token(db_path)

    data = _exact_get(token, division, "read/financial/ReceivablesList", params={
        "$top": max_results,
        "$orderby": "DueDate asc",
    })

    if not isinstance(data, dict):
        raise ValueError(f"Exact Online API onverwachte response: {str(data)[:200]}")
    items = (lambda d: d if isinstance(d, list) else d.get("results", []))(data.get("d", []))
    result = []
    for item in items:
        result.append({
            "klant": item.get("AccountName", ""),
            "bedrag": item.get("Amount"),
            "omschrijving": item.get("Description", ""),
            "vervaldatum": _format_exact_date(item.get("DueDate", "")),
            "factuurnummer": item.get("InvoiceNumber") or item.get("HID", ""),
        })
    return result


def get_recent_transactions(db_path: str, max_results: int = 10) -> List[Dict]:
    """Haal recente boekingen op."""
    token, division = _get_access_token(db_path)

    data = _exact_get(token, division, "financialtransaction/TransactionLines", params={
        "$select": "Date,Description,AmountDC,GLAccountDescription",
        "$top": max_results,
        "$orderby": "Date desc",
    })

    items = (lambda d: d if isinstance(d, list) else d.get("results", []))(data.get("d", []))
    result = []
    for item in items:
        result.append({
            "datum": _format_exact_date(item.get("Date", "")),
            "omschrijving": item.get("Description", ""),
            "bedrag": item.get("AmountDC"),
            "rekening": item.get("GLAccountDescription", ""),
        })
    return result
