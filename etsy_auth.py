import os
import time
import requests
from datetime import datetime, timedelta
from typing import Optional

from db import get_session
from models import OAuthToken

ETSY_CLIENT_ID = os.getenv("ETSY_CLIENT_ID")
ETSY_CLIENT_SECRET = os.getenv("ETSY_CLIENT_SECRET")
ETSY_REDIRECT_URI = os.getenv("ETSY_REDIRECT_URI", "http://localhost:8000/auth/etsy/callback")
BASE_URL = "https://openapi.etsy.com/v3/application"
AUTH_URL = "https://www.etsy.com/oauth/connect"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
SCOPES = [
    "listings_d", "shops_r", "shops_w", "email_r"  # adjust as needed
]


def etsy_auth_url(state: str) -> str:
    if not ETSY_CLIENT_ID:
        raise RuntimeError("ETSY_CLIENT_ID not set")
    params = {
        "response_type": "code",
        "client_id": ETSY_CLIENT_ID,
        "redirect_uri": ETSY_REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": state,
    }
    from urllib.parse import urlencode
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code(code: str) -> OAuthToken:
    if not (ETSY_CLIENT_ID and ETSY_CLIENT_SECRET):
        raise RuntimeError("ETSY client credentials not set")
    data = {
        "grant_type": "authorization_code",
        "client_id": ETSY_CLIENT_ID,
        "redirect_uri": ETSY_REDIRECT_URI,
        "code": code,
        "code_verifier": "automerch"  # if using PKCE, replace accordingly
    }
    auth = (ETSY_CLIENT_ID, ETSY_CLIENT_SECRET)
    r = requests.post(TOKEN_URL, data=data, auth=auth, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Etsy token exchange error {r.status_code}: {r.text}")
    tok = r.json()
    expires_in = int(tok.get("expires_in", 0))
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None
    with get_session() as s:
        # single token per provider
        existing = s.query(OAuthToken).filter(OAuthToken.provider == "etsy").first()
        if existing:
            existing.access_token = tok.get("access_token")
            existing.refresh_token = tok.get("refresh_token")
            existing.expires_at = expires_at
            s.add(existing)
            s.commit()
            return existing
        obj = OAuthToken(provider="etsy", access_token=tok.get("access_token"), refresh_token=tok.get("refresh_token"), expires_at=expires_at)
        s.add(obj)
        s.commit()
        s.refresh(obj)
        return obj


def refresh_token() -> Optional[OAuthToken]:
    if not (ETSY_CLIENT_ID and ETSY_CLIENT_SECRET):
        return None
    with get_session() as s:
        tok = s.query(OAuthToken).filter(OAuthToken.provider == "etsy").first()
        if not tok or not tok.refresh_token:
            return tok
        data = {
            "grant_type": "refresh_token",
            "client_id": ETSY_CLIENT_ID,
            "refresh_token": tok.refresh_token,
        }
        auth = (ETSY_CLIENT_ID, ETSY_CLIENT_SECRET)
        r = requests.post(TOKEN_URL, data=data, auth=auth, timeout=30)
        if r.status_code >= 400:
            return tok
        j = r.json()
        expires_in = int(j.get("expires_in", 0))
        tok.access_token = j.get("access_token")
        tok.refresh_token = j.get("refresh_token", tok.refresh_token)
        tok.expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else tok.expires_at
        s.add(tok)
        s.commit()
        return tok


def get_access_token() -> Optional[str]:
    # Prefer DB token; fall back to env ETSY_ACCESS_TOKEN
    with get_session() as s:
        tok = s.query(OAuthToken).filter(OAuthToken.provider == "etsy").first()
        if tok and tok.expires_at and tok.expires_at < datetime.utcnow():
            tok = refresh_token() or tok
        if tok and tok.access_token:
            return tok.access_token
    return os.getenv("ETSY_ACCESS_TOKEN")
