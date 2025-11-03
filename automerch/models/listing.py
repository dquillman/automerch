"""Listing model for tracking Etsy drafts."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Listing(SQLModel, table=True):
    """Tracks Etsy listing drafts and published listings."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: str = Field(unique=True, index=True)  # Etsy listing ID
    etsy_listing_id: Optional[str] = Field(default=None, index=True)  # Alias for listing_id
    sku: str = Field(index=True)  # Product SKU
    shop_id: Optional[str] = Field(default=None, index=True)  # Etsy shop ID
    title: str
    price: float
    status: str = Field(default="draft")  # draft, active, inactive
    etsy_url: Optional[str] = None  # URL to listing on Etsy
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


