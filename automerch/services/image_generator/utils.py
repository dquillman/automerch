"""Utilities for image handling and storage."""

import base64
from pathlib import Path
from typing import Optional
import logging
import requests

logger = logging.getLogger(__name__)


def save_image_from_base64(base64_data: str, output_path: Path, filename: str) -> Optional[Path]:
    """Save a base64 encoded image to disk.
    
    Args:
        base64_data: Base64 encoded image string
        output_path: Directory to save image in
        filename: Name of the file (without extension)
        
    Returns:
        Path to saved image, or None if failed
    """
    try:
        output_path.mkdir(parents=True, exist_ok=True)
        img_bytes = base64.b64decode(base64_data)
        
        # Detect image format from magic bytes
        if img_bytes.startswith(b'\xff\xd8\xff'):
            ext = 'jpg'
        elif img_bytes.startswith(b'\x89PNG'):
            ext = 'png'
        elif img_bytes.startswith(b'RIFF') and b'WEBP' in img_bytes[:12]:
            ext = 'webp'
        else:
            ext = 'jpg'  # Default
        
        file_path = output_path / f"{filename}.{ext}"
        file_path.write_bytes(img_bytes)
        return file_path
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        return None


def download_image_from_url(url: str, output_path: Path, filename: str) -> Optional[Path]:
    """Download an image from URL and save locally.
    
    Args:
        url: Image URL
        output_path: Directory to save image in
        filename: Name of the file (without extension)
        
    Returns:
        Path to saved image, or None if failed
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get extension from content type or URL
        content_type = response.headers.get('content-type', 'image/jpeg')
        if 'png' in content_type:
            ext = 'png'
        elif 'webp' in content_type:
            ext = 'webp'
        elif url.lower().endswith('.png'):
            ext = 'png'
        elif url.lower().endswith('.webp'):
            ext = 'webp'
        else:
            ext = 'jpg'
        
        file_path = output_path / f"{filename}.{ext}"
        file_path.write_bytes(response.content)
        return file_path
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {e}")
        return None

