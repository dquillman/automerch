import os
import requests

from etsy_auth import get_access_token

def _headers():
    token = get_access_token()
    if not token:
        raise RuntimeError("No Etsy access token; connect via Integrations page or set ETSY_ACCESS_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if not ETSY_ACCESS_TOKEN:
        raise RuntimeError("ETSY_ACCESS_TOKEN not set")
    return {
        "Authorization": f"Bearer {ETSY_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def create_listing_draft(product: dict) -> str:
    """
    Create a draft listing. Requires ETSY_SHOP_ID and a valid access token.
    Product dict should include at least: title, description, who_made, when_made, is_supply, taxonomy_id.
    In DRY_RUN mode returns a dummy listing id.
    """
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
        # taxonomy 1125 = T-shirts & tops (example). Adjust as needed.
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

