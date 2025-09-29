import os
import requests
from pathlib import Path

DRY_RUN = os.getenv("AUTOMERCH_DRY_RUN", "true").lower() == "true"
ETSY_SHOP_ID = os.getenv("ETSY_SHOP_ID")
BASE_URL = "https://openapi.etsy.com/v3/application"

from etsy_auth import get_access_token

def _headers():
    token = get_access_token()
    if not token:
        raise RuntimeError("No Etsy access token; connect via Integrations page or set ETSY_ACCESS_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def create_listing_draft(product: dict) -> str:
    if DRY_RUN:
        return "LISTING-DRYRUN"
    if not ETSY_SHOP_ID:
        raise RuntimeError("ETSY_SHOP_ID not set")
    payload = {
        "title": product.get("title") or f"Product {product.get('sku', '')}",
        "description": product.get("description", ""),
        "who_made": product.get("who_made", "i_did"),
        "when_made": product.get("when_made", "made_to_order"),
        "is_supply": product.get("is_supply", False),
        "taxonomy_id": product.get("taxonomy_id", 1125),
        "type": "physical",
        "should_auto_renew": False,
        "state": "draft",
        "is_personalizable": False,
    }
    url = f"{BASE_URL}/shops/{ETSY_SHOP_ID}/listings"
    r = requests.post(url, headers=_headers(), json=payload, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Etsy error {r.status_code}: {r.text}")
    data = r.json()
    listing_id = str(data.get("listing_id") or data.get("data", {}).get("listing_id") or "")
    return listing_id or "LISTING-UNKNOWN"


def publish_listing(listing_id: str) -> bool:
    if DRY_RUN:
        return True
    url = f"{BASE_URL}/listings/{listing_id}"
    r = requests.patch(url, headers=_headers(), json={"state": "active"}, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Etsy publish error {r.status_code}: {r.text}")
    return True


def upload_listing_image_from_url(listing_id: str, image_url: str) -> bool:
    if DRY_RUN:
        return True
    # Download image then upload via multipart
    resp = requests.get(image_url, timeout=30)
    resp.raise_for_status()
    return _upload_listing_image_bytes(listing_id, resp.content, file_name=Path(image_url).name or "image.jpg")


def upload_listing_image_from_file(listing_id: str, file_path: str) -> bool:
    if DRY_RUN:
        return True
    p = Path(file_path)
    data = p.read_bytes()
    return _upload_listing_image_bytes(listing_id, data, file_name=p.name)


def _upload_listing_image_bytes(listing_id: str, data: bytes, file_name: str) -> bool:
    url = f"{BASE_URL}/listings/{listing_id}/images"
    headers = _headers()
    headers.pop("Content-Type", None)
    files = {"image": (file_name, data, "application/octet-stream")}
    r = requests.post(url, headers=headers, files=files, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"Etsy image upload error {r.status_code}: {r.text}")
    return True
