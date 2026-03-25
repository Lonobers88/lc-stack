"""
Moneybird client voor lc-mail-service.
Gebruikt een persoonlijk API token (geen OAuth redirect nodig).

Setup door admin:
1. Log in op moneybird.com
2. Ga naar Instellingen → API → Nieuw token aanmaken
3. Sla op in de LC mail service via POST /moneybird/connect
"""

import json
import urllib.request
from typing import Any, Dict, List, Optional


MONEYBIRD_API_BASE = "https://moneybird.com/api/v2"


def _mb_get(token: str, administration_id: str, endpoint: str,
            params: Optional[Dict] = None) -> Any:
    url = f"{MONEYBIRD_API_BASE}/{administration_id}/{endpoint}.json"
    if params:
        import urllib.parse
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def test_connection(token: str) -> Dict:
    """Test de verbinding en haal administraties op."""
    req = urllib.request.Request(
        f"{MONEYBIRD_API_BASE}/administrations.json",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        administrations = json.loads(resp.read())

    if not administrations:
        raise ValueError("Geen administraties gevonden voor dit token")

    return administrations[0]  # Geef eerste administratie terug


def get_unpaid_invoices(token: str, administration_id: str,
                        max_results: int = 10) -> List[Dict]:
    """Haal onbetaalde verkoopfacturen op."""
    data = _mb_get(token, administration_id, "sales_invoices", params={
        "filter": "state:open",
        "per_page": max_results,
    })

    result = []
    for inv in (data if isinstance(data, list) else []):
        result.append({
            "nummer": inv.get("invoice_id", ""),
            "datum": inv.get("invoice_date", "")[:10],
            "vervaldatum": inv.get("due_date", "")[:10],
            "bedrag": inv.get("total_price_incl_tax", ""),
            "klant": inv.get("contact", {}).get("company_name", "") or
                     inv.get("contact", {}).get("firstname", ""),
            "omschrijving": inv.get("reference", ""),
        })
    return result


def get_recent_estimates(token: str, administration_id: str,
                         max_results: int = 5) -> List[Dict]:
    """Haal recente offertes op."""
    data = _mb_get(token, administration_id, "estimates", params={
        "per_page": max_results,
    })

    result = []
    for est in (data if isinstance(data, list) else []):
        result.append({
            "nummer": est.get("estimate_id", ""),
            "datum": est.get("estimate_date", "")[:10],
            "status": est.get("state", ""),
            "bedrag": est.get("total_price_incl_tax", ""),
            "klant": est.get("contact", {}).get("company_name", "") or
                     est.get("contact", {}).get("firstname", ""),
        })
    return result
