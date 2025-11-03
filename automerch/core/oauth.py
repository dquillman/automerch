"""OAuth2 authentication for Etsy."""

import requests
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

from .settings import settings
from .db import get_session
from ..models.token import OAuthToken

logger = logging.getLogger(__name__)


def get_authorization_url(state: str) -> str:
    """Generate Etsy OAuth authorization URL.
    
    Args:
        state: CSRF state token for security
        
    Returns:
        Authorization URL
    """
    if not settings.ETSY_CLIENT_ID:
        raise RuntimeError("ETSY_CLIENT_ID not set in environment")
    
    params = {
        "response_type": "code",
        "client_id": settings.ETSY_CLIENT_ID,
        "redirect_uri": settings.ETSY_REDIRECT_URI,
        "scope": " ".join(settings.ETSY_SCOPES),
        "state": state,
    }
    return f"{settings.ETSY_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str, shop_id: Optional[str] = None) -> OAuthToken:
    """Exchange authorization code for access and refresh tokens.
    
    Args:
        code: Authorization code from OAuth callback
        shop_id: Optional shop ID (if None, will try to get from token)
        
    Returns:
        OAuthToken object with tokens
    """
    if not (settings.ETSY_CLIENT_ID and settings.ETSY_CLIENT_SECRET):
        raise RuntimeError("Etsy client credentials not set")
    
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.ETSY_CLIENT_ID,
        "redirect_uri": settings.ETSY_REDIRECT_URI,
        "code": code,
    }
    
    auth = (settings.ETSY_CLIENT_ID, settings.ETSY_CLIENT_SECRET)
    response = requests.post(
        settings.ETSY_TOKEN_URL,
        data=data,
        auth=auth,
        timeout=30
    )
    
    if response.status_code >= 400:
        raise RuntimeError(
            f"Etsy token exchange error {response.status_code}: {response.text}"
        )
    
    token_data = response.json()
    expires_in = int(token_data.get("expires_in", 0))
    expires_at = (
        datetime.utcnow() + timedelta(seconds=expires_in) 
        if expires_in 
        else None
    )
    
    # Try to get shop ID from token metadata or API if not provided
    shops_data = None
    if not shop_id:
        # Get shop ID from Etsy API using the access token
        try:
            access_token = token_data.get("access_token")
            shop_response = requests.get(
                f"{settings.ETSY_API_BASE}/shops",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            if shop_response.status_code == 200:
                shops_data = shop_response.json()
                if shops_data.get("results") and len(shops_data["results"]) > 0:
                    shop_id = str(shops_data["results"][0].get("shop_id", ""))
        except Exception as e:
            logger.warning(f"Could not determine shop ID: {e}")
    
    # Store or update token in database (per shop)
    with next(get_session()) as session:
        from sqlmodel import select
        from ..models.shop import EtsyShop
        
        # Find existing token for this shop
        if shop_id:
            existing = session.exec(
                select(OAuthToken).where(
                    OAuthToken.provider == "etsy",
                    OAuthToken.shop_id == shop_id
                )
            ).first()
        else:
            # Legacy: find token without shop_id
            existing = session.exec(
                select(OAuthToken).where(
                    OAuthToken.provider == "etsy",
                    OAuthToken.shop_id.is_(None)
                )
            ).first()
        
        if existing:
            existing.access_token = token_data.get("access_token")
            existing.refresh_token = token_data.get("refresh_token")
            existing.expires_at = expires_at
            if shop_id:
                existing.shop_id = shop_id
            existing.updated_at = datetime.utcnow()
            session.add(existing)
            session.commit()
            session.refresh(existing)
            
            # Create or update shop record
            if shop_id:
                shop = session.get(EtsyShop, shop_id)
                if not shop:
                    shop = EtsyShop(
                        shop_id=shop_id,
                        shop_name=shops_data.get("results", [{}])[0].get("shop_name") if shop_id else None,
                        shop_url=f"https://www.etsy.com/shop/{shop_id}" if shop_id else None
                    )
                    session.add(shop)
                    session.commit()
            
            return existing
        
        token_obj = OAuthToken(
            provider="etsy",
            shop_id=shop_id,
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            expires_at=expires_at
        )
        session.add(token_obj)
        
        # Create shop record if shop_id exists
        if shop_id:
            shop = session.get(EtsyShop, shop_id)
            if not shop:
                shop_name = None
                if 'shops_data' in locals() and shops_data.get("results"):
                    shop_name = shops_data["results"][0].get("shop_name")
                shop = EtsyShop(
                    shop_id=shop_id,
                    shop_name=shop_name,
                    shop_url=f"https://www.etsy.com/shop/{shop_id}"
                )
                session.add(shop)
        
        session.commit()
        session.refresh(token_obj)
        return token_obj


def refresh_access_token(shop_id: Optional[str] = None) -> Optional[OAuthToken]:
    """Refresh the access token using refresh token.
    
    Args:
        shop_id: Optional shop ID (None for legacy single-shop)
        
    Returns:
        Updated OAuthToken or None if refresh fails
    """
    if not (settings.ETSY_CLIENT_ID and settings.ETSY_CLIENT_SECRET):
        return None
    
    with next(get_session()) as session:
        from sqlmodel import select
        if shop_id:
            token = session.exec(
                select(OAuthToken).where(
                    OAuthToken.provider == "etsy",
                    OAuthToken.shop_id == shop_id
                )
            ).first()
        else:
            # Legacy: try to find token without shop_id, or use default shop
            token = session.exec(
                select(OAuthToken).where(
                    OAuthToken.provider == "etsy",
                    OAuthToken.shop_id.is_(None)
                )
            ).first()
            
            # If no legacy token, try to find default shop
            if not token:
                from ..models.shop import EtsyShop
                default_shop = session.exec(
                    select(EtsyShop).where(EtsyShop.is_default == True)
                ).first()
                if default_shop:
                    token = session.exec(
                        select(OAuthToken).where(
                            OAuthToken.provider == "etsy",
                            OAuthToken.shop_id == default_shop.shop_id
                        )
                    ).first()
        
        if not token or not token.refresh_token:
            return token
        
        data = {
            "grant_type": "refresh_token",
            "client_id": settings.ETSY_CLIENT_ID,
            "refresh_token": token.refresh_token,
        }
        
        auth = (settings.ETSY_CLIENT_ID, settings.ETSY_CLIENT_SECRET)
        response = requests.post(
            settings.ETSY_TOKEN_URL,
            data=data,
            auth=auth,
            timeout=30
        )
        
        if response.status_code >= 400:
            return token
        
        token_data = response.json()
        expires_in = int(token_data.get("expires_in", 0))
        
        token.access_token = token_data.get("access_token")
        token.refresh_token = token_data.get("refresh_token", token.refresh_token)
        if expires_in:
            token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        token.updated_at = datetime.utcnow()
        
        session.add(token)
        session.commit()
        return token


def get_access_token(shop_id: Optional[str] = None) -> Optional[str]:
    """Get current access token, refreshing if expired.
    
    Args:
        shop_id: Optional shop ID (None for default/legacy)
        
    Returns:
        Access token string or None
    """
    with next(get_session()) as session:
        from sqlmodel import select
        from ..models.shop import EtsyShop
        
        if shop_id:
            token = session.exec(
                select(OAuthToken).where(
                    OAuthToken.provider == "etsy",
                    OAuthToken.shop_id == shop_id
                )
            ).first()
        else:
            # Try default shop first
            default_shop = session.exec(
                select(EtsyShop).where(EtsyShop.is_default == True)
            ).first()
            
            if default_shop:
                token = session.exec(
                    select(OAuthToken).where(
                        OAuthToken.provider == "etsy",
                        OAuthToken.shop_id == default_shop.shop_id
                    )
                ).first()
            else:
                # Legacy: token without shop_id
                token = session.exec(
                    select(OAuthToken).where(
                        OAuthToken.provider == "etsy",
                        OAuthToken.shop_id.is_(None)
                    )
                ).first()
        
        # Refresh if expired
        if token and token.expires_at and token.expires_at < datetime.utcnow():
            token = refresh_access_token(shop_id=token.shop_id) or token
        
        if token and token.access_token:
            return token.access_token
    
    # Fallback to environment variable
    import os
    return os.getenv("ETSY_ACCESS_TOKEN")

