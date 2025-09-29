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

def update_listing(listing_id: str, fields: dict) -> bool:
    """Update listing title/description; price usually needs inventory APIs."""
    if os.getenv("AUTOMERCH_DRY_RUN", "true").lower() == "true":
        return True
    url = f"{BASE_URL}/listings/{listing_id}"
    allowed = {k: fields[k] for k in ("title", "description", "who_made", "when_made", "is_supply") if k in fields and fields[k] is not None}
    if not allowed:
        return True
    r = requests.patch(url, headers=_headers(), json=allowed, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Etsy update error {r.status_code}: {r.text}")
    return True

def update_listing_price(listing_id: str, price: float, currency: str = "USD", quantity: int = 999) -> bool:
    if DRY_RUN:
        return True
    url = f"{BASE_URL}/listings/{listing_id}/inventory"
    body = {
        "products": [
            {
                "offerings": [
                    {
                        "price": {"amount": int(round(price * 100)), "currency_code": currency},
                        "quantity": quantity
                    }
                ]
            }
        ]
    }
    r = requests.put(url, headers=_headers(), json=body, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Etsy inventory error {r.status_code}: {r.text}")
    return True


def search_listings(keywords: str, limit: int = 50, offset: int = 0, sort_on: str = "score") -> list[dict]:
    """Search active Etsy listings for given keywords.

    Note: Etsy API may change; this uses the public v3 application listings search.
    """
    if DRY_RUN:
        # Return a small mock when dry-run to allow downstream logic to work.
        return [
            {"listing_id": 1, "title": f"{keywords} Funny Gift Mug", "price": {"amount": 1599, "currency_code": "USD"}, "tags": ["mug", "funny", "gift"]},
            {"listing_id": 2, "title": f"{keywords} Minimalist T-Shirt", "price": {"amount": 2199, "currency_code": "USD"}, "tags": ["t-shirt", "minimal", "unisex"]},
        ]
    params = {
        "keywords": keywords,
        "limit": limit,
        "offset": offset,
        "sort_on": sort_on,
        # "category": category,  # optionally add category filtering
    }
    url = f"{BASE_URL}/listings/active"
    r = requests.get(url, headers=_headers(), params=params, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Etsy search error {r.status_code}: {r.text}")
    data = r.json()
    # Some responses return { "results": [...] }, others top-level list
    if isinstance(data, dict) and "results" in data:
        return data["results"] or []
    if isinstance(data, list):
        return data
    return []
