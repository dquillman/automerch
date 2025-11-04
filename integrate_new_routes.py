"""Integration script to merge new AutoMerch Lite routes into existing app.py.

This creates a bridge between the old and new code structure.
"""

import sys
from pathlib import Path

# This script modifies app.py to include new routes
# Run: python integrate_new_routes.py

def integrate_routes():
    """Add new routes to existing app.py."""
    
    app_py_path = Path(__file__).parent / "app.py"
    
    if not app_py_path.exists():
        print("❌ app.py not found")
        return False
    
    content = app_py_path.read_text()
    
    # Check if already integrated
    if "from automerch.api.routes" in content:
        print("✅ Routes already integrated")
        return True
    
    # Find where to insert (after FastAPI app creation)
    insert_marker = 'app = FastAPI(title="AutoMerch")'
    
    if insert_marker not in content:
        print("❌ Could not find app creation in app.py")
        return False
    
    # Prepare integration code
    integration_code = '''
# AutoMerch Lite Integration
try:
    from automerch.api.routes import auth, drafts, assets, ui
    from automerch.api.dependencies import get_etsy_client
    
    # Include new routers
    app.include_router(auth.router)
    app.include_router(drafts.router)
    app.include_router(assets.router)
    app.include_router(ui.router)
    
    print("✅ AutoMerch Lite routes integrated")
except ImportError as e:
    print(f"⚠️  AutoMerch Lite routes not available: {e}")
'''
    
    # Insert after app creation
    new_content = content.replace(
        insert_marker,
        insert_marker + integration_code
    )
    
    # Also add helper function to use new services in existing routes
    helper_code = '''

# Helper function to use new Etsy drafts service
def create_etsy_draft_v2(product_data: dict) -> dict:
    """Create Etsy draft using new service layer."""
    try:
        from automerch.services.etsy.drafts import EtsyDraftsService
        from automerch.api.dependencies import get_etsy_client
        
        client = get_etsy_client()
        service = EtsyDraftsService(client)
        
        return service.create_draft(
            title=product_data.get("title") or product_data.get("name", ""),
            description=product_data.get("description", ""),
            price=product_data.get("price", 19.99),
            taxonomy_id=product_data.get("taxonomy_id", 6947),
            tags=product_data.get("tags", []),
            images=product_data.get("images")
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create draft: {e}")
'''
    
    # Add helper before the last line
    if "if __name__" in new_content:
        new_content = new_content.replace(
            "\nif __name__",
            helper_code + "\nif __name__"
        )
    else:
        new_content += helper_code
    
    # Write back
    app_py_path.write_text(new_content)
    print("✅ Successfully integrated AutoMerch Lite routes")
    print("   New endpoints available at:")
    print("   - /api/drafts/*")
    print("   - /auth/etsy/*")
    print("   - /drafts (UI)")
    return True


if __name__ == "__main__":
    success = integrate_routes()
    sys.exit(0 if success else 1)





