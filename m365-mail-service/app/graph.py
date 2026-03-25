import json
from typing import Any, Dict, Optional

import httpx
import msal

from .config import get_settings
from .db import load_mailbox_token, update_mailbox_token


def _build_public_msal_app() -> msal.PublicClientApplication:
    settings = get_settings()
    authority = f"https://login.microsoftonline.com/{settings.tenant_id}"
    return msal.PublicClientApplication(
        settings.client_id,
        authority=authority,
    )


def init_device_flow() -> Dict[str, Any]:
    settings = get_settings()
    app = _build_public_msal_app()
    # Filter out reserved scopes for device flow - MSAL handles these automatically
    scopes = [s for s in settings.scopes if s not in ["offline_access", "openid", "profile"]]
    flow = app.initiate_device_flow(scopes=scopes)
    return flow


def acquire_token_by_device_flow(device_code: str) -> Optional[Dict[str, Any]]:
    settings = get_settings()
    app = _build_public_msal_app()
    result = app.acquire_token_by_device_flow({"device_code": device_code})
    if "access_token" in result:
        return result
    elif "error" in result and result["error"] == "authorization_pending":
        return None
    elif "error" in result:
        raise RuntimeError(f"Device flow error: {result.get('error_description', result['error'])}")
    return None


def get_access_token(mailbox: Dict[str, Any]) -> str:
    settings = get_settings()
    app = _build_public_msal_app()
    token = load_mailbox_token(mailbox)
    refresh_token = token.get("refresh_token")
    if not refresh_token:
        raise RuntimeError("Missing refresh_token for mailbox")
    new_token = app.acquire_token_by_refresh_token(refresh_token, scopes=settings.scopes)
    if "access_token" not in new_token:
        raise RuntimeError(f"Failed to refresh token: {json.dumps(new_token)}")
    update_mailbox_token(mailbox["id"], new_token)
    return new_token["access_token"]


def graph_get(access_token: str, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    settings = get_settings()
    url = f"{settings.graph_base}{path}"
    headers = {"Authorization": f"Bearer {access_token}"}
    with httpx.Client(timeout=20) as client:
        resp = client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()


def graph_post(access_token: str, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    settings = get_settings()
    url = f"{settings.graph_base}{path}"
    headers = {"Authorization": f"Bearer {access_token}"}
    with httpx.Client(timeout=20) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()
