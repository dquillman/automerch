"""Asset model for tracking product assets."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Asset(SQLModel, table=True):
    """Tracks product assets (mockups, print files, etc.)."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(index=True)  # Product SKU
    asset_type: str = Field(default="mockup")  # mockup, print_file, image
    drive_url: Optional[str] = None  # Google Drive URL
    local_path: Optional[str] = None  # Local file path
    created_at: datetime = Field(default_factory=datetime.utcnow)





