"""Printful API client."""

import logging
from typing import Optional, Dict, Any, List
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from ...core.settings import settings

logger = logging.getLogger(__name__)


class PrintfulClient:
    """Client for Printful API v2."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Printful client.
        
        Args:
            api_key: Optional API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.PRINTFUL_API_KEY
        self.base_url = settings.PRINTFUL_API_BASE
    
    def _headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        if not self.api_key:
            if settings.AUTOMERCH_DRY_RUN:
                return {"Content-Type": "application/json"}
            raise RuntimeError("PRINTFUL_API_KEY not set")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        timeout: int = 60
    ) -> requests.Response:
        """Make authenticated HTTP request to Printful API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            json_data: JSON body data
            timeout: Request timeout in seconds
            
        Returns:
            Response object
            
        Raises:
            RuntimeError: On API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._headers()
        
        if settings.AUTOMERCH_DRY_RUN and method in ("POST", "PUT", "DELETE"):
            logger.info(f"[DRY RUN] {method} {url}")
            # Return mock response for dry run
            class MockResponse:
                status_code = 200
                def json(self):
                    return {
                        "code": 200,
                        "result": {
                            "sync_product": {"id": 12345, "name": "Dry Run Product"},
                            "sync_variant": {"id": "VARIANT-DRYRUN-123"}
                        }
                    }
                @property
                def text(self):
                    return '{"code": 200, "result": {"sync_product": {"id": 12345}}}'
            return MockResponse()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=timeout
            )
            
            if response.status_code >= 400:
                error_msg = f"Printful API error {response.status_code}: {response.text[:500]}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            logger.debug(f"{method} {url} - {response.status_code}")
            return response
            
        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"Printful API request timeout: {e}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Printful API request failed: {e}")
    
    def create_product(
        self,
        name: str,
        thumbnail: str,
        sku: str,
        variant_id: int,
        retail_price: float,
        design_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a sync product in Printful store.
        
        Args:
            name: Product name
            thumbnail: Thumbnail image URL
            sku: Product SKU
            variant_id: Printful variant ID (e.g., 4011 for mugs)
            retail_price: Retail price in USD
            design_url: Optional design file URL
            
        Returns:
            Dictionary with sync_product and sync_variant data
        """
        payload = {
            "sync_product": {
                "name": name,
                "thumbnail": thumbnail,
                "external_id": sku,
            },
            "sync_variants": [
                {
                    "retail_price": str(retail_price),
                    "sku": sku,
                    "variant_id": variant_id,
                    "files": []
                }
            ]
        }
        
        # Add design file if provided
        if design_url:
            payload["sync_variants"][0]["files"] = [
                {
                    "type": "preview",
                    "url": design_url
                }
            ]
        elif thumbnail:
            payload["sync_variants"][0]["files"] = [
                {
                    "type": "preview",
                    "url": thumbnail
                }
            ]
        
        response = self._request("POST", "/store/products", json_data=payload)
        result = response.json().get("result", {})
        
        return {
            "sync_product": result.get("sync_product", {}),
            "sync_variant": result.get("sync_variant", {}),
            "variant_id": str(result.get("sync_variant", {}).get("id", "")),
            "product_id": result.get("sync_product", {}).get("id")
        }
    
    def create_product_with_variants(
        self,
        name: str,
        thumbnail: str,
        sku: str,
        variants: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create a product with multiple variants.
        
        Args:
            name: Product name
            thumbnail: Thumbnail image URL
            sku: Base product SKU
            variants: List of variant dicts with keys:
                - retail_price (str): Price
                - sku (str): Variant SKU
                - variant_id (int): Printful variant ID
                - files (list): List of file dicts with type and url
                
        Returns:
            List of created variant info
        """
        payload = {
            "sync_product": {
                "name": name,
                "thumbnail": thumbnail,
                "external_id": sku,
            },
            "sync_variants": variants
        }
        
        response = self._request("POST", "/store/products", json_data=payload)
        result = response.json().get("result", {})
        
        # Return variant info based on what we sent
        created_variants = result.get("sync_variants", [])
        output = []
        for i, variant in enumerate(variants):
            created = created_variants[i] if i < len(created_variants) else {}
            output.append({
                "sku": variant.get("sku"),
                "variant_id": str(created.get("id", variant.get("variant_id", "")))
            })
        
        return output
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get sync product details.
        
        Args:
            product_id: Printful sync product ID
            
        Returns:
            Product data
        """
        response = self._request("GET", f"/store/products/{product_id}")
        return response.json().get("result", {})
    
    def get_product_variants(self, product_id: int) -> List[Dict[str, Any]]:
        """Get all variants for a sync product.
        
        Args:
            product_id: Printful sync product ID
            
        Returns:
            List of variant data
        """
        response = self._request("GET", f"/store/products/{product_id}")
        product = response.json().get("result", {}).get("sync_product", {})
        variants = product.get("sync_variants", [])
        return variants
    
    def get_catalog_variants(self, product_id: int) -> List[Dict[str, Any]]:
        """Get available catalog variants for a product template.
        
        Args:
            product_id: Printful catalog product ID (e.g., 71 for mugs)
            
        Returns:
            List of available variant options
        """
        if settings.AUTOMERCH_DRY_RUN:
            return [
                {"id": 4011, "name": "11oz Mug", "color": "White"},
                {"id": 4012, "name": "15oz Mug", "color": "White"}
            ]
        
        response = self._request("GET", f"/catalog/products/{product_id}")
        result = response.json().get("result", {})
        variants = []
        
        # Extract variant information from catalog product
        for variant in result.get("variants", []):
            variants.append({
                "id": variant.get("id"),
                "name": variant.get("name"),
                "color": variant.get("color"),
                "size": variant.get("size")
            })
        
        return variants
    
    def create_mockup(
        self,
        sync_product_id: int,
        sync_variant_id: Optional[int] = None,
        format: str = "jpg",
        width: int = 1000
    ) -> Dict[str, Any]:
        """Generate product mockup.
        
        Args:
            sync_product_id: Printful sync product ID
            sync_variant_id: Optional specific variant ID
            format: Image format (jpg or png)
            width: Image width in pixels
            
        Returns:
            Mockup data with URLs
        """
        if settings.AUTOMERCH_DRY_RUN:
            logger.info(f"[DRY RUN] Creating mockup for product {sync_product_id}")
            return {
                "mockup_url": "https://example.com/mockup.jpg",
                "placement": "front"
            }
        
        # Printful mockup generation endpoint
        endpoint = f"/mockup-generator/create-task/{sync_product_id}"
        if sync_variant_id:
            endpoint += f"/{sync_variant_id}"
        
        payload = {
            "format": format,
            "width": width
        }
        
        response = self._request("POST", endpoint, json_data=payload)
        result = response.json().get("result", {})
        
        return {
            "task_key": result.get("task_key"),
            "mockup_url": result.get("mockup_url"),
            "placement": result.get("placement", "front")
        }
    
    def get_store_info(self) -> Dict[str, Any]:
        """Get store information and metrics.
        
        Returns:
            Store data dictionary
        """
        if settings.AUTOMERCH_DRY_RUN:
            return {
                "name": "Dry Run Store",
                "currency": "USD",
                "email": "dryrun@example.com"
            }
        
        response = self._request("GET", "/store")
        result = response.json().get("result", {})
        
        return {
            "name": result.get("name"),
            "currency": result.get("currency"),
            "email": result.get("email"),
            "website": result.get("website")
        }
    
    def get_orders(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get store orders.
        
        Args:
            limit: Maximum number of orders to return
            offset: Number of orders to skip
            
        Returns:
            List of order data
        """
        if settings.AUTOMERCH_DRY_RUN:
            return []
        
        params = {"limit": limit, "offset": offset}
        response = self._request("GET", "/orders", params=params)
        result = response.json().get("result", {})
        
        return result.get("data", [])
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a sync product.
        
        Args:
            product_id: Printful sync product ID
            
        Returns:
            True if successful
        """
        if settings.AUTOMERCH_DRY_RUN:
            logger.info(f"[DRY RUN] Deleting product {product_id}")
            return True
        
        response = self._request("DELETE", f"/store/products/{product_id}")
        return response.status_code < 400