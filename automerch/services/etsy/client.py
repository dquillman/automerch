"""Etsy API client with authenticated HTTP requests."""

import time
import logging
from typing import Optional, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from ...core.settings import settings
from ...core.oauth import get_access_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EtsyClient:
    """Authenticated HTTP client for Etsy API v3."""
    
    def __init__(self, access_token: Optional[str] = None, shop_id: Optional[str] = None):
        """Initialize Etsy client.
        
        Args:
            access_token: Optional access token. If not provided, uses get_access_token()
            shop_id: Optional shop ID for multi-shop support
        """
        self.base_url = settings.ETSY_API_BASE
        self.shop_id = shop_id
        
        # In dry-run mode, allow dummy token
        if settings.AUTOMERCH_DRY_RUN and (access_token == "dry-run-token" or not access_token):
            self.access_token = "dry-run-token"
        else:
            self.access_token = access_token or get_access_token(shop_id=shop_id)
            if not self.access_token:
                raise RuntimeError(
                    f"No Etsy access token for shop {shop_id or 'default'}. Connect via OAuth or set ETSY_ACCESS_TOKEN."
                )
    
    def _headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
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
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        files: Optional[dict] = None,
        timeout: int = 30,
        retries: int = 3
    ) -> requests.Response:
        """Make authenticated HTTP request with rate limit handling and retries.
        
        Args:
            method: HTTP method (GET, POST, PATCH, PUT)
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            json_data: JSON body data
            files: Files for multipart upload
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            
        Returns:
            Response object
            
        Raises:
            RuntimeError: On API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._headers()
        
        # Remove Content-Type for file uploads
        if files:
            headers.pop("Content-Type", None)
        
        if settings.AUTOMERCH_DRY_RUN:
            logger.info(f"[DRY RUN] {method} {url}")
            # Return mock response for dry run with unique ID
            import random
            unique_id = random.randint(100000, 999999)
            mock_listing_id = f"DRY-RUN-{unique_id}"
            class MockResponse:
                status_code = 200
                def json(self):
                    return {"listing_id": mock_listing_id}
                @property
                def text(self):
                    return f'{{"listing_id": "{mock_listing_id}"}}'
            return MockResponse()
        
        last_exception = None
        for attempt in range(retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    files=files,
                    timeout=timeout
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 10))
                    logger.warning(
                        f"Rate limited (attempt {attempt + 1}/{retries}). "
                        f"Waiting {retry_after}s..."
                    )
                    time.sleep(retry_after)
                    continue
                
                # Handle server errors (5xx) with retry
                if 500 <= response.status_code < 600 and attempt < retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        f"Server error {response.status_code} (attempt {attempt + 1}/{retries}). "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                
                if response.status_code >= 400:
                    error_msg = (
                        f"Etsy API error {response.status_code}: {response.text[:500]}"
                    )
                    logger.error(f"{error_msg} (attempt {attempt + 1}/{retries})")
                    
                    # Don't retry on client errors (4xx) except 429
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        raise RuntimeError(error_msg)
                    
                    # Last attempt, raise error
                    if attempt == retries - 1:
                        raise RuntimeError(error_msg)
                
                # Success
                logger.debug(f"{method} {url} - {response.status_code}")
                return response
                
            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        f"Request timeout (attempt {attempt + 1}/{retries}). "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"Request timeout after {retries} attempts: {e}")
            
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        f"Request error (attempt {attempt + 1}/{retries}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"Request failed after {retries} attempts: {e}")
        
        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError(f"Request failed after {retries} attempts")
    
    def create_listing_draft(self, payload: dict[str, Any]) -> str:
        """Create a draft listing on Etsy.
        
        Args:
            payload: Listing data (title, description, price, taxonomy_id, etc.)
            
        Returns:
            Listing ID as string
        """
        # Use shop_id from client instance, payload, or settings
        shop_id = payload.get("shop_id") or self.shop_id or settings.ETSY_SHOP_ID
        
        if not shop_id:
            if settings.AUTOMERCH_DRY_RUN:
                shop_id = "dry-run-shop-12345"
            else:
                raise RuntimeError("shop_id required. Set in payload, client, or ETSY_SHOP_ID env var")
        
        listing_payload = {
            "title": payload.get("title", ""),
            "description": payload.get("description", ""),
            "who_made": payload.get("who_made", "i_did"),
            "when_made": payload.get("when_made", "made_to_order"),
            "is_supply": payload.get("is_supply", False),
            "taxonomy_id": payload.get("taxonomy_id", 1125),  # Default to mugs
            "type": "physical",
            "should_auto_renew": False,
            "state": "draft",  # Important: create as draft
            "is_personalizable": False,
        }
        
        # Add tags if provided
        if payload.get("tags"):
            listing_payload["tags"] = payload["tags"]
        
        # Set price via inventory endpoint (required by Etsy)
        # First create draft, then set price
        response = self._request(
            "POST",
            f"/shops/{shop_id}/listings",
            json_data=listing_payload
        )
        
        data = response.json()
        listing_id = str(data.get("listing_id") or "")
        
        if not listing_id:
            raise RuntimeError("Failed to get listing_id from response")
        
        # Set price via inventory API
        if payload.get("price"):
            try:
                self.update_listing_price(listing_id, payload["price"])
            except Exception as e:
                logger.warning(f"Failed to set price for listing {listing_id}: {e}")
        
        return listing_id
    
    def upload_listing_image(self, listing_id: str, image_path: str) -> bool:
        """Upload an image to a listing.
        
        Args:
            listing_id: Etsy listing ID
            image_path: Path to image file or URL
            
        Returns:
            True if successful
        """
        from pathlib import Path
        import tempfile
        
        # Handle URL vs file path
        if image_path.startswith("http://") or image_path.startswith("https://"):
            # Download image first
            resp = requests.get(image_path, timeout=30)
            resp.raise_for_status()
            image_data = resp.content
            file_name = Path(image_path).name or "image.jpg"
        else:
            image_data = Path(image_path).read_bytes()
            file_name = Path(image_path).name
        
        files = {"image": (file_name, image_data, "image/jpeg")}
        
        response = self._request(
            "POST",
            f"/listings/{listing_id}/images",
            files=files,
            timeout=60
        )
        
        return response.status_code < 400
    
    def get_listing(self, listing_id: str) -> dict[str, Any]:
        """Get listing details.
        
        Args:
            listing_id: Etsy listing ID
            
        Returns:
            Listing data dictionary
        """
        response = self._request("GET", f"/listings/{listing_id}")
        return response.json()
    
    def update_listing(self, listing_id: str, fields: dict[str, Any]) -> bool:
        """Update listing fields.
        
        Args:
            listing_id: Etsy listing ID
            fields: Fields to update (title, description, etc.)
            
        Returns:
            True if successful
        """
        allowed_fields = {
            k: v for k, v in fields.items()
            if k in ("title", "description", "who_made", "when_made", "is_supply", "tags")
        }
        
        if not allowed_fields:
            return True
        
        response = self._request(
            "PATCH",
            f"/listings/{listing_id}",
            json_data=allowed_fields
        )
        
        return response.status_code < 400
    
    def update_listing_price(self, listing_id: str, price: float, currency: str = "USD", quantity: int = 999) -> bool:
        """Update listing price via inventory API.
        
        Args:
            listing_id: Etsy listing ID
            price: Price in dollars
            currency: Currency code (default USD)
            quantity: Stock quantity (default 999)
            
        Returns:
            True if successful
        """
        payload = {
            "products": [
                {
                    "offerings": [
                        {
                            "price": {
                                "amount": int(round(price * 100)),
                                "currency_code": currency
                            },
                            "quantity": quantity
                        }
                    ]
                }
            ]
        }
        
        response = self._request(
            "PUT",
            f"/listings/{listing_id}/inventory",
            json_data=payload
        )
        
        return response.status_code < 400

