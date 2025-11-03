#!/usr/bin/env python3
"""Example: Create a single Etsy draft listing.

Usage:
    python examples/create_single_draft.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from automerch.services.etsy.drafts import EtsyDraftsService
from automerch.api.dependencies import get_etsy_client


def main():
    """Create a single draft listing."""
    print("🚀 Creating Etsy draft listing...")
    
    try:
        # Get authenticated client
        client = get_etsy_client()
        service = EtsyDraftsService(client)
        
        # Create draft
        result = service.create_draft(
            title="ENFP Coffee Mug - Adventure Awaits",
            description=(
                "Vibrant 11oz ceramic mug perfect for creative dreamers. "
                "This beautiful mug features an inspiring design that celebrates "
                "the ENFP personality type. Perfect for coffee lovers who embrace "
                "adventure and creativity.\n\n"
                "• High-quality ceramic construction\n"
                "• Dishwasher and microwave safe\n"
                "• Perfect gift for ENFP friends and family"
            ),
            price=14.99,
            taxonomy_id=6947,  # Coffee mugs
            tags=["enfp", "coffee", "mug", "gift", "personality", "creative"],
            images=[
                # Add your image URLs or paths here
                # "https://example.com/mockup1.jpg",
                # "https://example.com/mockup2.jpg",
            ]
        )
        
        print("\n✅ Draft created successfully!")
        print(f"   Listing ID: {result['listing_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Etsy URL: {result['etsy_url']}")
        print("\n📝 Next steps:")
        print("   1. Visit the Etsy URL above")
        print("   2. Review the draft in Etsy Shop Manager")
        print("   3. Assign shipping profile")
        print("   4. Publish when ready")
        
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Make sure you've completed OAuth: /auth/etsy/login")
        print("   - Check that ETSY_SHOP_ID is set in .env")
        print("   - Verify AUTOMERCH_DRY_RUN is set correctly")
        return 1
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


