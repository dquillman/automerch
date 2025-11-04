"""Test research image downloads."""

from research import run_research
from pathlib import Path

print("Testing research image downloads...")
print("=" * 60)

result = run_research('test product', limit=3)

print(f"\nResearch returned {len(result.get('listings', []))} listings\n")

listings = result.get('listings', [])
for i, listing in enumerate(listings):
    print(f"Listing {i+1}:")
    print(f"  Title: {listing.get('title', 'N/A')}")
    print(f"  Image URL: {listing.get('image_url', 'N/A')}")
    print(f"  Has base64: {listing.get('image_data_base64') is not None}")
    print(f"  Local path: {listing.get('image_local_path', 'N/A')}")

# Check research_images folder
img_dir = Path('research_images')
print(f"\n{'='*60}")
print(f"Images directory exists: {img_dir.exists()}")
if img_dir.exists():
    files = [f for f in img_dir.glob('*') if f.is_file()]
    print(f"Image files found: {len(files)}")
    for f in files[:5]:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")
else:
    print("No images directory yet")

print("\nDone!")




