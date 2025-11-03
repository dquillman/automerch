"""Etsy draft listing service."""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .client import EtsyClient

logger = logging.getLogger(__name__)


class EtsyDraftsService:
    """Service for creating and managing Etsy draft listings."""
    
    def __init__(self, client: Optional[EtsyClient] = None):
        """Initialize drafts service.
        
        Args:
            client: Optional EtsyClient. Creates new one if not provided.
        """
        self.client = client or EtsyClient()
    
    def create_draft(
        self,
        title: str,
        description: str,
        price: float,
        taxonomy_id: int = 6947,  # Coffee mugs default
        tags: Optional[List[str]] = None,
        images: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a draft listing with images.
        
        Args:
            title: Listing title
            description: Listing description
            price: Price in USD
            taxonomy_id: Etsy taxonomy ID (default 6947 for coffee mugs)
            tags: List of tags
            images: List of image paths or URLs
            **kwargs: Additional listing fields
            
        Returns:
            Dictionary with listing_id, etsy_url, status
        """
        # Build payload
        payload = {
            "title": title,
            "description": description,
            "price": price,
            "taxonomy_id": taxonomy_id,
            "tags": tags or [],
            **kwargs
        }
        
        # Create draft listing
        logger.info(f"Creating draft listing: {title}")
        listing_id = self.client.create_listing_draft(payload)
        
        # Upload images if provided
        if images:
            logger.info(f"Uploading {len(images)} images to listing {listing_id}")
            for idx, image_path in enumerate(images[:10]):  # Etsy allows up to 10 images
                try:
                    self.client.upload_listing_image(listing_id, image_path)
                    logger.info(f"Uploaded image {idx + 1}/{len(images)}")
                except Exception as e:
                    logger.error(f"Failed to upload image {image_path}: {e}")
        
        # Get listing details
        try:
            listing_data = self.client.get_listing(listing_id)
            etsy_url = listing_data.get("url") or f"https://www.etsy.com/listing/{listing_id}"
        except Exception:
            etsy_url = f"https://www.etsy.com/listing/{listing_id}"
        
        return {
            "listing_id": listing_id,
            "etsy_url": etsy_url,
            "status": "draft"
        }
    
    def create_draft_from_product(
        self,
        sku: str,
        product_data: Dict[str, Any],
        images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create draft from product data.
        
        Args:
            sku: Product SKU
            product_data: Product data dictionary
            images: Optional list of image paths/URLs
            
        Returns:
            Dictionary with listing_id, etsy_url, status
        """
        return self.create_draft(
            title=product_data.get("title") or product_data.get("name") or sku,
            description=product_data.get("description") or "",
            price=product_data.get("price", 19.99),
            taxonomy_id=product_data.get("taxonomy_id", 6947),
            tags=product_data.get("tags", []),
            images=images or ([product_data.get("thumbnail_url")] if product_data.get("thumbnail_url") else None)
        )


