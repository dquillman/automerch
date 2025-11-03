"""FastAPI dependencies."""

from typing import Annotated, Optional
from fastapi import Depends, Query

from ..services.etsy.client import EtsyClient
from ..services.printful.client import PrintfulClient
from ..core.oauth import get_access_token
from ..core.db import get_session


def get_etsy_client(shop_id: Optional[str] = None) -> EtsyClient:
    """Dependency to get authenticated EtsyClient.
    
    Args:
        shop_id: Optional shop ID from query parameter
        
    Returns:
        Authenticated EtsyClient
    """
    from fastapi import HTTPException
    from ..core.settings import settings
    
    # If no shop_id provided, try to get default shop
    if not shop_id:
        try:
            with next(get_session()) as session:
                from sqlmodel import select
                from ..models.shop import EtsyShop
                
                default_shop = session.exec(
                    select(EtsyShop).where(EtsyShop.is_default == True)
                ).first()
                if default_shop:
                    shop_id = default_shop.shop_id
        except Exception:
            pass
    
    # In dry-run mode, use a dummy token - API calls won't actually execute
    if settings.AUTOMERCH_DRY_RUN:
        try:
            token = get_access_token(shop_id=shop_id)
            if not token:
                # Use dummy token for dry-run mode
                token = "dry-run-token"
        except:
            token = "dry-run-token"
    else:
        # In live mode, require real token
        token = get_access_token(shop_id=shop_id)
        if not token:
            shop_msg = f" for shop {shop_id}" if shop_id else ""
            raise HTTPException(
                status_code=401,
                detail=f"No Etsy access token{shop_msg}. Please authenticate first at /auth/etsy/login"
            )
    
    try:
        return EtsyClient(access_token=token, shop_id=shop_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Etsy client: {str(e)}"
        )


def get_printful_client() -> PrintfulClient:
    """Dependency to get PrintfulClient."""
    from fastapi import HTTPException
    from ..core.settings import settings
    
    # In dry-run mode, allow missing API key
    if not settings.PRINTFUL_API_KEY and not settings.AUTOMERCH_DRY_RUN:
        raise HTTPException(
            status_code=401,
            detail="PRINTFUL_API_KEY not set. Please configure it in your .env file"
        )
    
    try:
        return PrintfulClient(api_key=settings.PRINTFUL_API_KEY)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Printful client: {str(e)}"
        )


# Helper function to get shop_id from query params
def get_shop_id_from_query(shop_id: Optional[str] = Query(None, description="Etsy shop ID")) -> Optional[str]:
    """Get shop_id from query parameter."""
    return shop_id


# Dependency factory for EtsyClient with shop_id support
def create_etsy_client_dependency(shop_id: Optional[str] = None):
    """Factory to create EtsyClient dependency with shop_id."""
    def _get_client():
        return get_etsy_client(shop_id=shop_id)
    return _get_client


# Type aliases for dependency injection
EtsyClientDep = Annotated[EtsyClient, Depends(get_etsy_client)]
PrintfulClientDep = Annotated[PrintfulClient, Depends(get_printful_client)]
ShopIDDep = Annotated[Optional[str], Depends(get_shop_id_from_query)]

