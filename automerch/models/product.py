"""Product model."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    """Product/SKU model."""
    
    sku: str = Field(primary_key=True)
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    thumbnail_url: Optional[str] = None
    variant_id: Optional[int] = None  # Printful catalog variant id
    printful_variant_id: Optional[str] = None
    etsy_listing_id: Optional[str] = None
    quantity: Optional[int] = None
    printful_file_id: Optional[int] = None
    # New fields for draft workflow
    taxonomy_id: Optional[int] = None  # Etsy taxonomy ID
    tags: Optional[str] = None  # Comma-separated tags





