from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    sku: str = Field(primary_key=True)
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    thumbnail_url: Optional[str] = None
    variant_id: Optional[int] = None  # Printful catalog variant id
    printful_variant_id: Optional[str] = None
    etsy_listing_id: Optional[str] = None


class RunLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job: str = Field(default="manual")
    status: str = Field(default="ok")
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OAuthToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
