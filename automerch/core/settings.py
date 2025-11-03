"""Application settings and configuration."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Etsy OAuth Configuration
    ETSY_CLIENT_ID: Optional[str] = os.getenv("ETSY_CLIENT_ID")
    ETSY_CLIENT_SECRET: Optional[str] = os.getenv("ETSY_CLIENT_SECRET")
    ETSY_REDIRECT_URI: str = os.getenv(
        "ETSY_REDIRECT_URI", 
        "http://localhost:8000/auth/etsy/callback"
    )
    ETSY_SHOP_ID: Optional[str] = os.getenv("ETSY_SHOP_ID")
    
    # Required OAuth scopes
    ETSY_SCOPES: list[str] = [
        "listings_r",
        "listings_w", 
        "shops_r",
        "profile_r"
    ]
    
    # Printful Configuration
    PRINTFUL_API_KEY: Optional[str] = os.getenv("PRINTFUL_API_KEY")
    
    # Google Drive Configuration
    GOOGLE_SVC_JSON: Optional[str] = os.getenv("GOOGLE_SVC_JSON")
    
    # Database Configuration
    AUTOMERCH_DB: str = os.getenv("AUTOMERCH_DB", "sqlite:///automerch.db")
    
    # Dry Run Mode
    AUTOMERCH_DRY_RUN: bool = os.getenv("AUTOMERCH_DRY_RUN", "true").lower() == "true"
    
    # Etsy API Base URLs
    ETSY_API_BASE: str = "https://openapi.etsy.com/v3/application"
    ETSY_AUTH_URL: str = "https://www.etsy.com/oauth/connect"
    ETSY_TOKEN_URL: str = "https://api.etsy.com/v3/public/oauth/token"
    
    # Printful API Base URL
    PRINTFUL_API_BASE: str = "https://api.printful.com"


# Global settings instance
settings = Settings()


