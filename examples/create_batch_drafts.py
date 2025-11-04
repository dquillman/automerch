#!/usr/bin/env python3
"""Example: Create multiple Etsy drafts from a list.

Usage:
    python examples/create_batch_drafts.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automerch.services.etsy.drafts import EtsyDraftsService
from automerch.api.dependencies import get_etsy_client


def main():
    """Create multiple drafts from a list of products."""
    
    # Example products
    products = [
        {
            "sku": "MUG-ENFP-001",
            "title": "ENFP Coffee Mug - Adventure Awaits",
            "description": "Perfect for creative dreamers who love adventure.",
            "price": 14.99,
            "taxonomy_id": 6947,
            "tags": ["enfp", "coffee", "mug", "gift"]
        },
        {
            "sku": "MUG-INTJ-001",
            "title": "INTJ Coffee Mug - Mastermind",
            "description": "For strategic thinkers and master planners.",
            "price": 14.99,
            "taxonomy_id": 6947,
            "tags": ["intj", "coffee", "mug", "gift"]
        },
        {
            "sku": "TSHIRT-MINIMAL-001",
            "title": "Minimalist T-Shirt Design",
            "description": "Clean, simple design for everyday wear.",
            "price": 19.99,
            "taxonomy_id": 1125,  # T-shirts
            "tags": ["tshirt", "minimal", "simple"]
        }
    ]
    
    print(f"🚀 Creating {len(products)} draft listings...\n")
    
    try:
        client = get_etsy_client()
        service = EtsyDraftsService(client)
        
        results = []
        for i, product in enumerate(products, 1):
            print(f"[{i}/{len(products)}] Creating draft: {product['title']}")
            
            try:
                result = service.create_draft(
                    title=product["title"],
                    description=product["description"],
                    price=product["price"],
                    taxonomy_id=product["taxonomy_id"],
                    tags=product["tags"]
                )
                
                results.append({
                    "sku": product["sku"],
                    "status": "success",
                    "listing_id": result["listing_id"],
                    "etsy_url": result["etsy_url"]
                })
                
                print(f"   ✅ Created: {result['listing_id']}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results.append({
                    "sku": product["sku"],
                    "status": "error",
                    "error": str(e)
                })
            
            # Small delay between requests to avoid rate limits
            import time
            time.sleep(1)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Summary:")
        success = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - success
        
        print(f"   ✅ Successful: {success}")
        print(f"   ❌ Failed: {failed}")
        
        if success > 0:
            print("\n✅ Successful drafts:")
            for r in results:
                if r["status"] == "success":
                    print(f"   - {r['sku']}: {r['listing_id']}")
                    print(f"     {r['etsy_url']}")
        
        if failed > 0:
            print("\n❌ Failed drafts:")
            for r in results:
                if r["status"] == "error":
                    print(f"   - {r['sku']}: {r.get('error', 'Unknown error')}")
        
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





