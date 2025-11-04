"""Etsy shop model for multi-shop support."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class EtsyShop(SQLModel, table=True):
    """Etsy shop configuration."""
    
    shop_id: str = Field(primary_key=True)  # Etsy shop ID
    shop_name: Optional[str] = None  # Shop display name
    is_active: bool = Field(default=True)  # Whether shop is active
    is_default: bool = Field(default=False)  # Default shop for operations
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Optional metadata
    shop_url: Optional[str] = None
    description: Optional[str] = None




