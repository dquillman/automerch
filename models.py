from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import MetaData

# Use a separate metadata instance for old models to avoid conflicts
_old_metadata = MetaData()


class Product(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
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


class RunLog(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    job: str = Field(default="manual")
    status: str = Field(default="ok")
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OAuthToken(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    provider: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None


class ResearchSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keywords: str
    limit: int = Field(default=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metrics_json: Optional[str] = None
    llm_json: Optional[str] = None


class ProductVariant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_sku: str = Field(foreign_key="product.sku")
    size: Optional[str] = None
    color: Optional[str] = None
    printful_variant_id: Optional[int] = None


class VariantMap(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    size: Optional[str] = None
    color: Optional[str] = None
    printful_variant_id: int


class PricingRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="Global")
    active: bool = Field(default=True)
    margin_pct: float = Field(default=0.5)  # 50% margin over cost
    min_price: float = Field(default=9.99)
    max_price: float = Field(default=99.99)
    rounding: str = Field(default=".99")  # .99 or .95
