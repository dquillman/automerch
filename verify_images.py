"""Verify images are created and base64 is stored."""

from research import run_research
from pathlib import Path
import json

print("Running research...")
result = run_research('test', limit=2)

listings = result.get('listings', [])
print(f"\n✅ Research returned {len(listings)} listings\n")

for i, listing in enumerate(listings):
    print(f"Listing {i+1}: {listing.get('title', 'N/A')[:40]}")
    print(f"  Image URL: {listing.get('image_url', 'None')[:60]}...")
    print(f"  Has base64: {listing.get('image_data_base64') is not None}")
    print(f"  Base64 length: {len(listing.get('image_data_base64', ''))}")
    print(f"  Local path: {listing.get('image_local_path', 'None')}")

# Check folder
img_dir = Path('research_images')
if img_dir.exists():
    files = list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.png'))
    print(f"\n✅ Image files in folder: {len(files)}")
    for f in files[:5]:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")
else:
    print("\n❌ No research_images folder")

print("\n✅ Done!")




