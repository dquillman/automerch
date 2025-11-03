#!/usr/bin/env python3
"""Example: Create Etsy draft from existing product in database.

Usage:
    python examples/create_draft_from_product.py SKU
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automerch.services.etsy.drafts import EtsyDraftsService
from automerch.api.dependencies import get_etsy_client
from automerch.core.db import get_session
from automerch.models import Product


def main():
    """Create draft from product SKU."""
    if len(sys.argv) < 2:
        print("Usage: python create_draft_from_product.py SKU")
        print("\nExample:")
        print("  python create_draft_from_product.py MUG-001")
        return 1
    
    sku = sys.argv[1]
    print(f"🚀 Creating draft for product: {sku}")
    
    try:
        # Get product from database
        with next(get_session()) as session:
            from sqlmodel import select
            product = session.exec(
                select(Product).where(Product.sku == sku)
            ).first()
            
            if not product:
                print(f"❌ Product not found: {sku}")
                return 1
            
            print(f"   Found product: {product.name or sku}")
        
        # Get client and service
        client = get_etsy_client()
        service = EtsyDraftsService(client)
        
        # Create draft using product data
        result = service.create_draft_from_product(
            sku=sku,
            product_data={
                "title": product.name or sku,
                "description": product.description or "",
                "price": product.price or 19.99,
                "taxonomy_id": getattr(product, 'taxonomy_id', None) or 6947,
                "tags": (product.tags.split(",") if hasattr(product, 'tags') and product.tags else []),
                "thumbnail_url": product.thumbnail_url
            },
            images=[product.thumbnail_url] if product.thumbnail_url else None
        )
        
        # Update product with listing ID
        with next(get_session()) as session:
            product = session.get(Product, sku)
            if product:
                product.etsy_listing_id = result["listing_id"]
                session.add(product)
                
                # Create Listing record
                from automerch.models import Listing
                listing = Listing(
                    listing_id=result["listing_id"],
                    etsy_listing_id=result["listing_id"],
                    sku=sku,
                    title=product.name or sku,
                    price=product.price or 19.99,
                    status="draft",
                    etsy_url=result["etsy_url"]
                )
                session.add(listing)
                session.commit()
        
        print("\n✅ Draft created successfully!")
        print(f"   Listing ID: {result['listing_id']}")
        print(f"   Etsy URL: {result['etsy_url']}")
        
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


