"""Draft listing routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..dependencies import EtsyClientDep
from ...services.etsy.drafts import EtsyDraftsService
from ...core.db import get_session
from ...models import Listing, Product

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


class DraftRequest(BaseModel):
    """Request model for creating a draft."""
    sku: str = Field(..., description="Product SKU", min_length=1)
    title: str = Field(..., description="Listing title", min_length=1)
    description: str = Field(..., description="Listing description", min_length=1)
    price: float = Field(..., description="Price in USD", gt=0)
    taxonomy_id: int = Field(default=6947, description="Etsy taxonomy ID (6947 = coffee mugs)")
    tags: List[str] = Field(default_factory=list, description="Product tags")
    images: Optional[List[str]] = Field(default=None, description="List of image URLs")
    shop_id: Optional[str] = Field(default=None, description="Etsy shop ID (uses default if not provided)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sku": "MUG-001",
                "title": "Coffee Mug - Adventure Awaits",
                "description": "Beautiful 11oz ceramic mug perfect for coffee lovers",
                "price": 14.99,
                "taxonomy_id": 6947,
                "tags": ["mug", "coffee", "gift"],
                "images": None
            }
        }


class BatchDraftRequest(BaseModel):
    """Request model for batch draft creation."""
    drafts: List[DraftRequest]


class DraftResponse(BaseModel):
    """Response model for draft creation."""
    sku: str
    listing_id: str
    etsy_url: str
    status: str
    error: Optional[str] = None


@router.post("/new", response_model=DraftResponse, summary="Create a new listing draft")
def create_draft(request: DraftRequest, client: EtsyClientDep):
    """Create a single draft listing.
    
    Args:
        request: Draft creation request (can include shop_id)
        client: Authenticated EtsyClient (shop_id from query param or default)
        
    Returns:
        Draft response with listing ID and URL
    """
    try:
        # Use shop_id from request, client, or query param
        shop_id = request.shop_id or client.shop_id
        
        # Create client with specific shop if needed
        if shop_id and shop_id != client.shop_id:
            from ...api.dependencies import get_etsy_client
            client = get_etsy_client(shop_id=shop_id)
        
        drafts_service = EtsyDraftsService(client)
        result = drafts_service.create_draft(
            title=request.title,
            description=request.description,
            price=request.price,
            taxonomy_id=request.taxonomy_id,
            tags=request.tags,
            images=request.images
        )
        
        # Store in database
        with next(get_session()) as session:
            from sqlmodel import select
            
            # Check if listing already exists
            existing = session.exec(
                select(Listing).where(Listing.listing_id == result["listing_id"])
            ).first()
            
            if existing:
                # Update existing listing
                existing.title = request.title
                existing.price = request.price
                existing.status = result["status"]
                existing.etsy_url = result["etsy_url"]
                if shop_id:
                    existing.shop_id = shop_id
                session.add(existing)
            else:
                # Create new listing
                listing = Listing(
                    listing_id=result["listing_id"],
                    etsy_listing_id=result["listing_id"],
                    sku=request.sku,
                    shop_id=shop_id,
                    title=request.title,
                    price=request.price,
                    status=result["status"],
                    etsy_url=result["etsy_url"]
                )
                session.add(listing)
            
            # Update product with listing ID
            product = session.get(Product, request.sku)
            if product:
                product.etsy_listing_id = result["listing_id"]
                session.add(product)
            
            session.commit()
        
        return DraftResponse(
            sku=request.sku,
            listing_id=result["listing_id"],
            etsy_url=result["etsy_url"],
            status=result["status"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=List[DraftResponse])
def create_batch_drafts(request: BatchDraftRequest, client: EtsyClientDep):
    """Create multiple draft listings.
    
    Args:
        request: Batch draft creation request
        client: Authenticated EtsyClient
        
    Returns:
        List of draft responses
    """
    results = []
    drafts_service = EtsyDraftsService(client)
    
    for draft_request in request.drafts:
        try:
            result = drafts_service.create_draft(
                title=draft_request.title,
                description=draft_request.description,
                price=draft_request.price,
                taxonomy_id=draft_request.taxonomy_id,
                tags=draft_request.tags,
                images=draft_request.images
            )
            
            # Store in database
            with next(get_session()) as session:
                listing = Listing(
                    listing_id=result["listing_id"],
                    etsy_listing_id=result["listing_id"],
                    sku=draft_request.sku,
                    title=draft_request.title,
                    price=draft_request.price,
                    status=result["status"],
                    etsy_url=result["etsy_url"]
                )
                session.add(listing)
                
                # Update product
                product = session.get(Product, draft_request.sku)
                if product:
                    product.etsy_listing_id = result["listing_id"]
                    session.add(product)
                
                session.commit()
            
            results.append(DraftResponse(
                sku=draft_request.sku,
                listing_id=result["listing_id"],
                etsy_url=result["etsy_url"],
                status=result["status"]
            ))
        except Exception as e:
            results.append(DraftResponse(
                sku=draft_request.sku,
                listing_id="",
                etsy_url="",
                status="error",
                error=str(e)
            ))
    
    return results


@router.get("/queue")
def get_drafts_queue(skip: int = 0, limit: int = 100):
    """Get list of all drafts.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of drafts (compatible with UI frontend)
    """
    try:
        with next(get_session()) as session:
            from sqlmodel import select
            stmt = select(Listing).offset(skip).limit(limit).order_by(Listing.created_at.desc())
            listings = session.exec(stmt).all()
            
            drafts = [
                {
                    "listing_id": l.listing_id,
                    "sku": l.sku or "",
                    "title": l.title or "",
                    "price": float(l.price) if l.price else 0.0,
                    "status": l.status or "draft",
                    "etsy_url": l.etsy_url or "",
                    "created_at": l.created_at.isoformat() if l.created_at else None
                }
                for l in listings
            ]
            return drafts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get drafts: {str(e)}")


@router.get("/{listing_id}")
def get_draft(listing_id: str):
    """Get draft details.
    
    Args:
        listing_id: Etsy listing ID
        
    Returns:
        Draft details
    """
    with next(get_session()) as session:
        from sqlmodel import select
        listing = session.exec(
            select(Listing).where(Listing.listing_id == listing_id)
        ).first()
        
        if not listing:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        return {
            "listing_id": listing.listing_id,
            "sku": listing.sku,
            "title": listing.title,
            "price": listing.price,
            "status": listing.status,
            "etsy_url": listing.etsy_url,
            "created_at": listing.created_at.isoformat() if listing.created_at else None
        }

