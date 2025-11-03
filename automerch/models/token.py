"""OAuth token model."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, UniqueConstraint


class OAuthToken(SQLModel, table=True):
    """OAuth token storage for providers like Etsy."""
    
    __table_args__ = (
        UniqueConstraint("provider", "shop_id", name="unique_provider_shop"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    provider: str = Field(index=True)  # e.g., "etsy"
    shop_id: Optional[str] = Field(default=None, index=True)  # Etsy shop ID (None for legacy single-shop)
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


