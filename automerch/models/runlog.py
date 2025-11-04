"""Run log model for tracking job executions."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class RunLog(SQLModel, table=True):
    """Log entry for job runs and operations."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    job: str = Field(default="manual")
    status: str = Field(default="ok")
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)





