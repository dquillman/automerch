#!/usr/bin/env python3
"""Example: List all draft listings.

Usage:
    python examples/list_all_drafts.py
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from automerch.core.db import get_session
from automerch.models import Listing


def main():
    """List all drafts from database."""
    print("📋 Listing all drafts...\n")
    
    try:
        with next(get_session()) as session:
            from sqlmodel import select
            listings = session.exec(
                select(Listing).order_by(Listing.created_at.desc())
            ).all()
            
            if not listings:
                print("No drafts found.")
                return 0
            
            print(f"Found {len(listings)} draft(s):\n")
            print("=" * 80)
            
            for i, listing in enumerate(listings, 1):
                print(f"\n{i}. {listing.title}")
                print(f"   SKU: {listing.sku}")
                print(f"   Listing ID: {listing.listing_id}")
                print(f"   Price: ${listing.price:.2f}")
                print(f"   Status: {listing.status}")
                if listing.etsy_url:
                    print(f"   URL: {listing.etsy_url}")
                if listing.created_at:
                    print(f"   Created: {listing.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n" + "=" * 80)
            
            # Summary by status
            status_counts = {}
            for listing in listings:
                status_counts[listing.status] = status_counts.get(listing.status, 0) + 1
            
            print("\n📊 Summary by status:")
            for status, count in status_counts.items():
                print(f"   {status}: {count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


