"""Database configuration and session management."""

import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

from .settings import settings

# Create database engine
engine = create_engine(settings.AUTOMERCH_DB, echo=False)


def init_db():
    """Initialize database and create all tables."""
    # Import all models to register them with SQLModel
    from ..models import (
        Product, 
        RunLog, 
        OAuthToken,
        Listing,
        Asset,
        EtsyShop
    )
    
    # Use Alembic if configured
    if os.getenv("USE_ALEMBIC", "false").lower() == "true":
        try:
            from alembic import command
            from alembic.config import Config
            cfg = Config("alembic.ini")
            if settings.AUTOMERCH_DB:
                cfg.set_main_option("sqlalchemy.url", settings.AUTOMERCH_DB)
            command.upgrade(cfg, "head")
            return
        except Exception:
            pass
    
    # Otherwise create all tables and migrate existing ones
    SQLModel.metadata.create_all(engine)
    
    # Migrate existing tables if they exist
    _migrate_product_table()
    _migrate_oauth_token_table()
    _migrate_listing_table()


def _migrate_product_table():
    """Migrate existing Product table to add new columns if needed."""
    with engine.connect() as conn:
        try:
            # Check if product table exists
            result = conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='product'"
            )
            if not result.fetchone():
                return  # Table doesn't exist, will be created by SQLModel
            
            # Get existing columns
            result = conn.exec_driver_sql("PRAGMA table_info('product')")
            existing_cols = {row[1] for row in result}
            
            # Add missing columns
            if 'cost' not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE product ADD COLUMN cost FLOAT")
            if 'taxonomy_id' not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE product ADD COLUMN taxonomy_id INTEGER")
            if 'tags' not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE product ADD COLUMN tags VARCHAR")
            
            conn.commit()
        except Exception as e:
            # If migration fails, log but don't crash
            print(f"Warning: Product table migration had issues: {e}")


def _migrate_oauth_token_table():
    """Migrate OAuthToken table to add shop_id column."""
    with engine.connect() as conn:
        try:
            result = conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='oauthtoken'"
            )
            if not result.fetchone():
                return
            
            result = conn.exec_driver_sql("PRAGMA table_info('oauthtoken')")
            existing_cols = {row[1] for row in result}
            
            if 'shop_id' not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE oauthtoken ADD COLUMN shop_id VARCHAR")
            if 'created_at' not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE oauthtoken ADD COLUMN created_at TIMESTAMP")
            if 'updated_at' not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE oauthtoken ADD COLUMN updated_at TIMESTAMP")
            
            conn.commit()
        except Exception as e:
            print(f"Warning: OAuthToken table migration had issues: {e}")


def _migrate_listing_table():
    """Migrate Listing table to add shop_id column."""
    with engine.connect() as conn:
        try:
            result = conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='listing'"
            )
            if not result.fetchone():
                return
            
            result = conn.exec_driver_sql("PRAGMA table_info('listing')")
            existing_cols = {row[1] for row in result}
            
            if 'shop_id' not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE listing ADD COLUMN shop_id VARCHAR")
            
            conn.commit()
        except Exception as e:
            print(f"Warning: Listing table migration had issues: {e}")


def get_session() -> Generator[Session, None, None]:
    """Get a database session (context manager)."""
    with Session(engine) as session:
        yield session

