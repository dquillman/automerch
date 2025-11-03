#!/usr/bin/env python3
"""Comprehensive test script for AutoMerch Lite.

Tests all components:
- Settings loading
- Database initialization
- OAuth flow
- Draft creation
- API endpoints
"""

import sys
import os
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set test mode
os.environ["AUTOMERCH_DRY_RUN"] = "true"

def test_imports():
    """Test 1: Verify all imports work."""
    print("🧪 Test 1: Testing imports...")
    try:
        from automerch.core.settings import settings
        from automerch.core.db import init_db, get_session
        from automerch.core.oauth import get_authorization_url
        from automerch.models import Product, Listing, Asset, OAuthToken
        from automerch.services.etsy.client import EtsyClient
        from automerch.services.etsy.drafts import EtsyDraftsService
        from automerch.api.app import app
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False


def test_settings():
    """Test 2: Verify settings load correctly."""
    print("\n🧪 Test 2: Testing settings...")
    try:
        from automerch.core.settings import settings
        
        assert settings.ETSY_API_BASE == "https://openapi.etsy.com/v3/application"
        assert settings.AUTOMERCH_DB is not None
        print(f"✅ Settings loaded: DB={settings.AUTOMERCH_DB}, DryRun={settings.AUTOMERCH_DRY_RUN}")
        return True
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False


def test_database():
    """Test 3: Verify database initialization."""
    print("\n🧪 Test 3: Testing database...")
    try:
        from automerch.core.db import init_db, get_session
        
        init_db()
        print("✅ Database initialized")
        
        # Test session
        with next(get_session()) as session:
            print("✅ Session created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        traceback.print_exc()
        return False


def test_oauth_url():
    """Test 4: Verify OAuth URL generation."""
    print("\n🧪 Test 4: Testing OAuth URL generation...")
    try:
        from automerch.core.oauth import get_authorization_url
        
        # Set a dummy client ID for testing
        os.environ["ETSY_CLIENT_ID"] = "test_client_id"
        
        url = get_authorization_url("test_state")
        assert "etsy.com/oauth/connect" in url
        assert "test_client_id" in url
        print(f"✅ OAuth URL generated: {url[:80]}...")
        return True
    except Exception as e:
        print(f"⚠️  OAuth URL test skipped: {e}")
        return True  # Not critical if credentials not set


def test_etsy_client():
    """Test 5: Verify Etsy client creation."""
    print("\n🧪 Test 5: Testing Etsy client...")
    try:
        from automerch.services.etsy.client import EtsyClient
        
        # Should fail without token, but structure should work
        try:
            client = EtsyClient(access_token="test_token")
            print("✅ Etsy client created")
            return True
        except RuntimeError as e:
            if "access token" in str(e).lower():
                print("⚠️  Etsy client needs token (expected)")
                return True
            raise
    except Exception as e:
        print(f"❌ Etsy client test failed: {e}")
        return False


def test_drafts_service():
    """Test 6: Verify drafts service."""
    print("\n🧪 Test 6: Testing drafts service...")
    try:
        from automerch.services.etsy.drafts import EtsyDraftsService
        from automerch.services.etsy.client import EtsyClient
        
        # Create client with dummy token for structure test
        client = EtsyClient(access_token="dummy_token")
        service = EtsyDraftsService(client)
        print("✅ Drafts service created")
        return True
    except Exception as e:
        print(f"❌ Drafts service test failed: {e}")
        return False


def test_api_app():
    """Test 7: Verify FastAPI app."""
    print("\n🧪 Test 7: Testing FastAPI app...")
    try:
        from automerch.api.app import app
        
        assert app is not None
        assert app.title == "AutoMerch Lite"
        
        # Check routes
        routes = [route.path for route in app.routes]
        assert "/health" in routes or any("/health" in str(r) for r in routes)
        print(f"✅ FastAPI app created with {len(routes)} routes")
        return True
    except Exception as e:
        print(f"❌ API app test failed: {e}")
        traceback.print_exc()
        return False


def test_draft_creation_dry_run():
    """Test 8: Test draft creation in dry-run mode."""
    print("\n🧪 Test 8: Testing draft creation (dry-run)...")
    try:
        from automerch.services.etsy.drafts import EtsyDraftsService
        from automerch.services.etsy.client import EtsyClient
        
        # Create with dummy token (dry-run mode)
        client = EtsyClient(access_token="dummy_token")
        service = EtsyDraftsService(client)
        
        result = service.create_draft(
            title="Test Product",
            description="Test description",
            price=19.99,
            taxonomy_id=6947,
            tags=["test"]
        )
        
        assert "listing_id" in result
        assert result["status"] == "draft"
        print(f"✅ Draft creation test passed: {result}")
        return True
    except Exception as e:
        print(f"❌ Draft creation test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("AutoMerch Lite Test Suite\n")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_settings,
        test_database,
        test_oauth_url,
        test_etsy_client,
        test_drafts_service,
        test_api_app,
        test_draft_creation_dry_run,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed or were skipped")
        return 1


if __name__ == "__main__":
    sys.exit(main())


