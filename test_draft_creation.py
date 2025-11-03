#!/usr/bin/env python3
"""Quick test for draft creation after fixes."""
import requests
import json

url = "http://localhost:8000/api/drafts/new"

# Valid request payload
payload = {
    "sku": "TEST-VALID-001",
    "title": "Test Coffee Mug",
    "description": "A beautiful test mug",
    "price": 14.99,
    "taxonomy_id": 6947,
    "tags": ["test", "mug"],
    "images": None
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("\n✅ Draft created successfully!")
except Exception as e:
    print(f"❌ Error: {e}")

