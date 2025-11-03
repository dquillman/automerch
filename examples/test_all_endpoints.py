#!/usr/bin/env python3
"""Comprehensive test suite for all AutoMerch Lite endpoints."""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("\n" + "="*60)
    print("1. Testing Health Endpoint")
    print("="*60)
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Status: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_create_draft():
    """Test creating a single draft."""
    print("\n" + "="*60)
    print("2. Testing Create Draft (POST /api/drafts/new)")
    print("="*60)
    payload = {
        "sku": "TEST-001",
        "title": "Test Coffee Mug",
        "description": "A beautiful test mug",
        "price": 14.99,
        "taxonomy_id": 6947,
        "tags": ["test", "mug"],
        "images": None
    }
    try:
        r = requests.post(f"{BASE_URL}/api/drafts/new", json=payload)
        print(f"Status: {r.status_code}")
        response = r.json()
        print(f"Response: {json.dumps(response, indent=2)}")
        if r.status_code == 200:
            return response.get("listing_id")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_create_batch_drafts():
    """Test batch draft creation."""
    print("\n" + "="*60)
    print("3. Testing Batch Draft Creation (POST /api/drafts/batch)")
    print("="*60)
    payload = {
        "drafts": [
            {
                "sku": "TEST-BATCH-001",
                "title": "Batch Test Mug 1",
                "description": "First batch test mug",
                "price": 15.99,
                "taxonomy_id": 6947,
                "tags": ["batch", "test"],
                "images": None
            },
            {
                "sku": "TEST-BATCH-002",
                "title": "Batch Test Mug 2",
                "description": "Second batch test mug",
                "price": 16.99,
                "taxonomy_id": 6947,
                "tags": ["batch", "test"],
                "images": None
            }
        ]
    }
    try:
        r = requests.post(f"{BASE_URL}/api/drafts/batch", json=payload)
        print(f"Status: {r.status_code}")
        response = r.json()
        print(f"Response: {json.dumps(response, indent=2)}")
        if r.status_code == 200 and isinstance(response, list):
            return len(response)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0


def test_get_drafts_queue():
    """Test getting drafts queue."""
    print("\n" + "="*60)
    print("4. Testing Get Drafts Queue (GET /api/drafts/queue)")
    print("="*60)
    try:
        r = requests.get(f"{BASE_URL}/api/drafts/queue")
        print(f"Status: {r.status_code}")
        response = r.json()
        print(f"Total drafts: {len(response.get('drafts', []))}")
        print(f"Response (first 3): {json.dumps(response.get('drafts', [])[:3], indent=2)}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_single_draft(listing_id: str):
    """Test getting a single draft."""
    print("\n" + "="*60)
    print(f"5. Testing Get Single Draft (GET /api/drafts/{{listing_id}})")
    print("="*60)
    if not listing_id:
        print("⚠️  Skipping - no listing_id from previous test")
        return False
    try:
        r = requests.get(f"{BASE_URL}/api/drafts/{listing_id}")
        print(f"Status: {r.status_code}")
        response = r.json()
        print(f"Response: {json.dumps(response, indent=2)}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_upload_asset():
    """Test uploading asset metadata."""
    print("\n" + "="*60)
    print("6. Testing Upload Asset (POST /api/assets/upload)")
    print("="*60)
    params = {
        "sku": "TEST-001",
        "asset_type": "mockup",
        "drive_url": "https://drive.google.com/file/test123",
        "local_path": "/tmp/test.png"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/assets/upload", params=params)
        print(f"Status: {r.status_code}")
        response = r.json()
        print(f"Response: {json.dumps(response, indent=2)}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_assets():
    """Test getting assets for a SKU."""
    print("\n" + "="*60)
    print("7. Testing Get Assets (GET /api/assets/{sku})")
    print("="*60)
    sku = "TEST-001"
    try:
        r = requests.get(f"{BASE_URL}/api/assets/{sku}")
        print(f"Status: {r.status_code}")
        response = r.json()
        print(f"Assets found: {len(response)}")
        print(f"Response: {json.dumps(response, indent=2)}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_drafts_ui():
    """Test drafts UI page."""
    print("\n" + "="*60)
    print("8. Testing Drafts UI (GET /drafts)")
    print("="*60)
    try:
        r = requests.get(f"{BASE_URL}/drafts")
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        if "text/html" in r.headers.get('Content-Type', ''):
            print("✅ HTML page returned")
            print(f"Page length: {len(r.text)} characters")
            return True
        else:
            print(f"Response: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_auth_endpoints():
    """Test auth endpoints (login URL generation)."""
    print("\n" + "="*60)
    print("9. Testing Auth Endpoints")
    print("="*60)
    
    # Test login URL
    try:
        r = requests.get(f"{BASE_URL}/auth/etsy/login", allow_redirects=False)
        print(f"Login endpoint status: {r.status_code}")
        if r.status_code in [303, 302, 307]:
            print(f"✅ Redirects to: {r.headers.get('Location', 'N/A')}")
            return True
        else:
            print(f"Response: {r.text[:200]}")
            return r.status_code < 500  # Not a server error
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 AutoMerch Lite - Comprehensive Endpoint Tests")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print("\nMake sure the server is running:")
    print("  python run_automerch_lite.py --mode lite")
    
    results = {}
    
    # Run tests
    results["health"] = test_health()
    
    listing_id = test_create_draft()
    results["create_draft"] = listing_id is not None
    
    batch_count = test_create_batch_drafts()
    results["batch_drafts"] = batch_count > 0
    
    results["get_queue"] = test_get_drafts_queue()
    
    results["get_single"] = test_get_single_draft(listing_id)
    
    results["upload_asset"] = test_upload_asset()
    
    results["get_assets"] = test_get_assets()
    
    results["drafts_ui"] = test_drafts_ui()
    
    results["auth"] = test_auth_endpoints()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    run_all_tests()

