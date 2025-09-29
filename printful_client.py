import os
import requests

PRINTFUL_API_KEY = os.getenv("PRINTFUL_API_KEY")
DRY_RUN = os.getenv("AUTOMERCH_DRY_RUN", "true").lower() == "true"
BASE_URL = "https://api.printful.com"


def _headers():
    if not PRINTFUL_API_KEY:
        raise RuntimeError("PRINTFUL_API_KEY not set")
    return {
        "Authorization": f"Bearer {PRINTFUL_API_KEY}",
        "Content-Type": "application/json",
    }


def create_product(product: dict):
    """
    Create a product in Printful store. In DRY_RUN mode returns a dummy variant id and asset list.
    """
    if DRY_RUN:
        return "VARIANT-DRYRUN", ["https://example.com/hero.png"]

    # Minimal example payload; real payload depends on chosen print file/variant
    payload = {
        "sync_product": {
            "name": product.get("name") or product.get("sku", "AutoMerch Product"),
            "thumbnail": product.get("thumbnail"),
            "external_id": product.get("sku"),
        },
        "sync_variants": [
            {
                "retail_price": str(product.get("price") or "19.99"),
                "sku": product.get("sku"),
                # A catalog variant id is required; placeholder 4011 used as example only
                "variant_id": product.get("variant_id", 4011)
            }
        ],
    }
    r = requests.post(f"{BASE_URL}/store/products", headers=_headers(), json=payload, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Printful error {r.status_code}: {r.text}")
    data = r.json().get("result", {})
    variant_id = str((data.get("sync_variant") or {}).get("id") or "")
    assets = [data.get("sync_product", {}).get("thumbnail")] if data.get("sync_product") else []
    return variant_id or "VARIANT-UNKNOWN", [a for a in assets if a]


def get_store_metrics():
    if DRY_RUN:
        return {"orders": 0, "revenue": 0.0}
    r = requests.get(f"{BASE_URL}/store", headers=_headers(), timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Printful error {r.status_code}: {r.text}")
    data = r.json().get("result", {})
    return {"name": data.get("name"), "currency": data.get("currency")} 
