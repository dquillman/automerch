import os
import requests
from http_client import request as http_request

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
        "sync_variants": [\n            {\n                "retail_price": str(product.get("price") or "19.99"),\n                "sku": product.get("sku"),\n                "variant_id": product.get("variant_id", 4011),\n                "files": ([{"type": "preview", "url": product.get("thumbnail")} ] if product.get("thumbnail") else [])\n            }\n        ],\n    }
    r = http_request("POST", f"{BASE_URL}/store/products", headers=_headers(), json=payload, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Printful error {r.status_code}: {r.text}")
    data = r.json().get("result", {})
    variant_id = str((data.get("sync_variant") or {}).get("id") or "")
    assets = [data.get("sync_product", {}).get("thumbnail")] if data.get("sync_product") else []
    return variant_id or "VARIANT-UNKNOWN", [a for a in assets if a]


def get_store_metrics():
    if DRY_RUN:
        return {"orders": 0, "revenue": 0.0}
    r = http_request("GET", f"{BASE_URL}/store", headers=_headers(), timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Printful error {r.status_code}: {r.text}")
    data = r.json().get("result", {})
    return {"name": data.get("name"), "currency": data.get("currency")} 


def create_product_with_variants(product: dict, variants: list[dict]):
    """
    Create a product with multiple variants in Printful. Each variant dict should include
    {"retail_price": str, "sku": str, "variant_id": int, "files": [...]}.
    In DRY_RUN returns dummy IDs per variant.
    """
    if DRY_RUN:
        return [
            {"sku": v.get("sku"), "variant_id": f"VARIANT-DRYRUN-{i+1}"}
            for i, v in enumerate(variants)
        ]
    payload = {
        "sync_product": {
            "name": product.get("name") or product.get("sku", "AutoMerch Product"),
            "thumbnail": product.get("thumbnail"),
            "external_id": product.get("sku"),
        },
        "sync_variants": variants,
    }
    r = http_request("POST", f"{BASE_URL}/store/products", headers=_headers(), json=payload, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"Printful error {r.status_code}: {r.text}")
    data = r.json().get("result", {})
    # The API may return only the primary variant. We return SKUs we sent.
    out = []
    for v in variants:
        out.append({"sku": v.get("sku"), "variant_id": v.get("variant_id")})
    return out

