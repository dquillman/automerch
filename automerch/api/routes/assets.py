"""Asset management routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException

from ...core.db import get_session
from ...models import Asset

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.post("/upload")
def upload_asset(sku: str, asset_type: str = "mockup", drive_url: Optional[str] = None, local_path: Optional[str] = None):
    """Upload asset metadata to database.
    
    Args:
        sku: Product SKU
        asset_type: Type of asset (mockup, print_file, image)
        drive_url: Google Drive URL (optional)
        local_path: Local file path (optional)
        
    Returns:
        Asset ID
    """
    with next(get_session()) as session:
        asset = Asset(
            sku=sku,
            asset_type=asset_type,
            drive_url=drive_url,
            local_path=local_path
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        
        return {"id": asset.id, "sku": asset.sku, "asset_type": asset.asset_type}


@router.get("/{sku}")
def get_assets(sku: str):
    """Get all assets for a SKU.
    
    Args:
        sku: Product SKU
        
    Returns:
        List of assets
    """
    with next(get_session()) as session:
        from sqlmodel import select
        assets = session.exec(
            select(Asset).where(Asset.sku == sku)
        ).all()
        
        return [
            {
                "id": a.id,
                "sku": a.sku,
                "asset_type": a.asset_type,
                "drive_url": a.drive_url,
                "local_path": a.local_path,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in assets
        ]

