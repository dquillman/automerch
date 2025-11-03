"""Etsy shop management routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from ...core.db import get_session
from ...models.shop import EtsyShop

router = APIRouter(prefix="/api/shops", tags=["shops"])


class ShopRequest(BaseModel):
    """Shop creation/update request."""
    shop_id: str
    shop_name: Optional[str] = None
    is_active: bool = True
    is_default: bool = False
    shop_url: Optional[str] = None
    description: Optional[str] = None


@router.get("")
def list_shops(active_only: bool = False):
    """List all Etsy shops.
    
    Args:
        active_only: Only return active shops
        
    Returns:
        List of shops
    """
    try:
        with next(get_session()) as session:
            from sqlmodel import select
            stmt = select(EtsyShop)
            if active_only:
                stmt = stmt.where(EtsyShop.is_active == True)
            shops = session.exec(stmt.order_by(EtsyShop.created_at.desc())).all()
            
            return [
                {
                    "shop_id": s.shop_id,
                    "shop_name": s.shop_name,
                    "is_active": s.is_active,
                    "is_default": s.is_default,
                    "shop_url": s.shop_url,
                    "description": s.description,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "updated_at": s.updated_at.isoformat() if s.updated_at else None
                }
                for s in shops
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list shops: {str(e)}")


@router.get("/default")
def get_default_shop():
    """Get the default shop.
    
    Returns:
        Default shop or first shop if no default set
    """
    try:
        with next(get_session()) as session:
            from sqlmodel import select
            
            # Try to find default shop
            default_shop = session.exec(
                select(EtsyShop).where(EtsyShop.is_default == True)
            ).first()
            
            if not default_shop:
                # Get first active shop
                default_shop = session.exec(
                    select(EtsyShop).where(EtsyShop.is_active == True)
                ).first()
            
            if not default_shop:
                raise HTTPException(status_code=404, detail="No shops found")
            
            return {
                "shop_id": default_shop.shop_id,
                "shop_name": default_shop.shop_name,
                "is_active": default_shop.is_active,
                "is_default": default_shop.is_default,
                "shop_url": default_shop.shop_url
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get default shop: {str(e)}")


@router.get("/{shop_id}")
def get_shop(shop_id: str):
    """Get shop by ID.
    
    Args:
        shop_id: Etsy shop ID
        
    Returns:
        Shop details
    """
    try:
        with next(get_session()) as session:
            shop = session.get(EtsyShop, shop_id)
            if not shop:
                raise HTTPException(status_code=404, detail="Shop not found")
            
            return {
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "is_active": shop.is_active,
                "is_default": shop.is_default,
                "shop_url": shop.shop_url,
                "description": shop.description,
                "created_at": shop.created_at.isoformat() if shop.created_at else None,
                "updated_at": shop.updated_at.isoformat() if shop.updated_at else None
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get shop: {str(e)}")


@router.post("")
def create_or_update_shop(shop: ShopRequest):
    """Create or update a shop.
    
    Args:
        shop: Shop data
        
    Returns:
        Created/updated shop
    """
    try:
        with next(get_session()) as session:
            db_shop = session.get(EtsyShop, shop.shop_id) or EtsyShop(shop_id=shop.shop_id)
            
            if shop.shop_name:
                db_shop.shop_name = shop.shop_name
            db_shop.is_active = shop.is_active
            db_shop.is_default = shop.is_default
            if shop.shop_url:
                db_shop.shop_url = shop.shop_url
            if shop.description:
                db_shop.description = shop.description
            db_shop.updated_at = datetime.utcnow()
            
            # If setting as default, unset other defaults
            if shop.is_default:
                from sqlmodel import select
                other_shops = session.exec(
                    select(EtsyShop).where(
                        EtsyShop.is_default == True,
                        EtsyShop.shop_id != shop.shop_id
                    )
                ).all()
                for other in other_shops:
                    other.is_default = False
                    session.add(other)
            
            session.add(db_shop)
            session.commit()
            session.refresh(db_shop)
            
            return {
                "shop_id": db_shop.shop_id,
                "shop_name": db_shop.shop_name,
                "is_active": db_shop.is_active,
                "is_default": db_shop.is_default,
                "status": "created" if not db_shop.created_at else "updated"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create/update shop: {str(e)}")


@router.delete("/{shop_id}")
def delete_shop(shop_id: str):
    """Delete a shop.
    
    Args:
        shop_id: Etsy shop ID
        
    Returns:
        Success message
    """
    try:
        with next(get_session()) as session:
            shop = session.get(EtsyShop, shop_id)
            if not shop:
                raise HTTPException(status_code=404, detail="Shop not found")
            
            session.delete(shop)
            session.commit()
            
            return {"status": "deleted", "shop_id": shop_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete shop: {str(e)}")


@router.post("/{shop_id}/set-default")
def set_default_shop(shop_id: str):
    """Set a shop as the default.
    
    Args:
        shop_id: Etsy shop ID
        
    Returns:
        Updated shop
    """
    try:
        with next(get_session()) as session:
            from sqlmodel import select
            
            shop = session.get(EtsyShop, shop_id)
            if not shop:
                raise HTTPException(status_code=404, detail="Shop not found")
            
            # Unset other defaults
            other_shops = session.exec(
                select(EtsyShop).where(
                    EtsyShop.is_default == True,
                    EtsyShop.shop_id != shop_id
                )
            ).all()
            for other in other_shops:
                other.is_default = False
                session.add(other)
            
            # Set this shop as default
            shop.is_default = True
            shop.updated_at = datetime.utcnow()
            session.add(shop)
            session.commit()
            session.refresh(shop)
            
            return {
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "is_default": shop.is_default,
                "status": "updated"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set default shop: {str(e)}")

