"""Test script to see what Etsy API actually returns for images."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from etsy_client import search_listings
import json

# Test search
keywords = "coffee mug"
limit = 3

print(f"Searching for: {keywords}")
print("=" * 60)

listings = search_listings(keywords, limit=limit)

for i, listing in enumerate(listings[:3]):
    print(f"\nListing {i+1}:")
    print(f"  ID: {listing.get('listing_id')}")
    print(f"  Title: {listing.get('title', 'N/A')[:50]}")
    print(f"\n  All keys in listing: {list(listing.keys())[:20]}")
    
    # Check for image fields
    print(f"\n  Image-related fields:")
    for key in listing.keys():
        if 'image' in key.lower() or 'url' in key.lower() or 'photo' in key.lower():
            value = listing[key]
            if isinstance(value, str):
                print(f"    {key}: {value[:80]}...")
            elif isinstance(value, (list, dict)):
                print(f"    {key}: {type(value).__name__} with {len(value) if hasattr(value, '__len__') else 'N/A'} items")
            else:
                print(f"    {key}: {type(value).__name__}")
    
    # Pretty print images field if it exists
    if 'images' in listing:
        print(f"\n  Images field structure:")
        print(f"    Type: {type(listing['images'])}")
        if isinstance(listing['images'], list):
            print(f"    Length: {len(listing['images'])}")
            if len(listing['images']) > 0:
                print(f"    First image type: {type(listing['images'][0])}")
                if isinstance(listing['images'][0], dict):
                    print(f"    First image keys: {list(listing['images'][0].keys())}")
                    print(f"    First image data: {json.dumps(listing['images'][0], indent=6)[:200]}")
        elif isinstance(listing['images'], dict):
            print(f"    Dict keys: {list(listing['images'].keys())}")
    
    print("\n" + "-" * 60)




