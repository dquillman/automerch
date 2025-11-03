"""Image generation client for creating product images."""

import logging
import os
from typing import Optional, Any
import requests
import base64
from io import BytesIO

from ...core.settings import settings

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Client for generating product images using AI APIs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize image generator.
        
        Args:
            api_key: API key for image generation service. If not provided, uses settings.
        """
        # Support multiple providers
        # Google's image generation is called "Imagen" (not Gemini - Gemini is for text)
        # For now, we'll use Vertex AI Imagen API or fallback to other services
        self.provider = os.getenv("IMAGE_GEN_PROVIDER", "google_imagen")  # google_imagen, openai_dalle, stability_ai
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("VERTEX_AI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("STABILITY_API_KEY")
        
    def generate_product_images(
        self,
        prompt: str,
        count: int = 5,
        style: str = "professional",
        aspect_ratio: str = "1:1",
        reference_image_url: Optional[str] = None,
        reference_image_base64: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Generate product images based on a prompt.
        
        Args:
            prompt: Description of the product/image to generate
            count: Number of images to generate (default: 5)
            style: Style of images (professional, artistic, minimal, etc.)
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:3, etc.)
            
        Returns:
            List of generated image data (urls, base64, or file paths)
        """
        # Add reference image info to prompt
        enhanced_prompt = prompt
        if reference_image_url or reference_image_base64:
            enhanced_prompt = f"{prompt}, improve upon this reference design, make it better and more appealing"
        
        if settings.AUTOMERCH_DRY_RUN or not self.api_key:
            logger.info(f"[DRY RUN] Generating {count} images with prompt: {enhanced_prompt[:50]}...")
            if reference_image_url:
                logger.info(f"[DRY RUN] Using reference image: {reference_image_url[:50]}...")
            # Return mock images (even in dry-run, we show the process works)
            return [
                {
                    "url": f"https://via.placeholder.com/800x800/4a90e2/ffffff?text=Improved+Image+{i+1}",
                    "prompt": enhanced_prompt,
                    "style": style,
                    "aspect_ratio": aspect_ratio,
                    "reference_image": reference_image_url or "base64_image"
                }
                for i in range(count)
            ]
        
        try:
            if self.provider in ("google_imagen", "google_imagen", "google_gemini"):
                return self._generate_with_imagen(prompt, count, style, aspect_ratio, reference_image_url, reference_image_base64)
            elif self.provider == "openai_dalle":
                return self._generate_with_dalle(prompt, count, style, aspect_ratio, reference_image_url, reference_image_base64)
            elif self.provider == "stability_ai":
                return self._generate_with_stability(prompt, count, style, aspect_ratio, reference_image_url, reference_image_base64)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
    
    def _generate_with_imagen(self, prompt: str, count: int, style: str, aspect_ratio: str, reference_image_url: Optional[str] = None, reference_image_base64: Optional[str] = None) -> list[dict[str, Any]]:
        """Generate images using Google Gemini image generation.
        
        Note: Google Gemini now supports image generation via the gemini-2.5-flash-image model.
        This is easier than Vertex AI Imagen setup.
        """
        try:
            # Try new Gemini image generation API
            try:
                from google import genai
                from google.genai import types
                
                enhanced_prompt = f"{prompt}, {style} style, aspect ratio {aspect_ratio}, high quality product image, printable design"
                
                client = genai.Client(api_key=self.api_key)
                images = []
                
                # Prepare content with reference image if provided
                contents = [enhanced_prompt]
                if reference_image_base64:
                    # Add image as part of the prompt
                    import io
                    from PIL import Image
                    img_bytes = base64.b64decode(reference_image_base64)
                    img = Image.open(io.BytesIO(img_bytes))
                    # Gemini can accept images in the content
                    contents.append(img)
                    enhanced_prompt = f"Create 5 improved variations of this product design: {prompt}. Make them better, more appealing, and professional. Style: {style}"
                elif reference_image_url:
                    # Download and add image
                    try:
                        img_resp = requests.get(reference_image_url, timeout=10)
                        if img_resp.status_code == 200:
                            from PIL import Image
                            import io
                            img = Image.open(io.BytesIO(img_resp.content))
                            contents.append(img)
                            enhanced_prompt = f"Create 5 improved variations of this product design: {prompt}. Make them better, more appealing, and professional. Style: {style}"
                    except Exception as e:
                        logger.warning(f"Could not load reference image: {e}")
                
                for i in range(count):
                    try:
                        # Use Gemini 2.0 Flash model with image input
                        response = client.models.generate_content(
                            model="gemini-2.0-flash-exp",
                            contents=contents,
                        )
                        
                        # Extract image data from response
                        if response.candidates and len(response.candidates) > 0:
                            for part in response.candidates[0].content.parts:
                                if part.inline_data is not None:
                                    img_base64 = part.inline_data.data
                                    images.append({
                                        "url": None,
                                        "base64": img_base64,
                                        "prompt": enhanced_prompt,
                                        "style": style,
                                        "aspect_ratio": aspect_ratio
                                    })
                                elif hasattr(part, 'text') and part.text:
                                    # If text response, might contain image URL
                                    logger.info(f"Gemini returned text: {part.text[:100]}")
                    except Exception as e:
                        logger.warning(f"Gemini image {i+1} generation failed: {e}")
                        continue
                
                return images if images else self._generate_mock_images(prompt, count, style, aspect_ratio)
                
            except ImportError:
                # Fallback to older google-generativeai package
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    
                    enhanced_prompt = f"{prompt}, {style} style, aspect ratio {aspect_ratio}, high quality product image"
                    images = []
                    
                    # Note: Older package might not support image generation directly
                    # Would need Vertex AI for actual generation
                    logger.warning("Using older Gemini API. Image generation may require Vertex AI Imagen.")
                    return self._generate_mock_images(prompt, count, style, aspect_ratio)
                    
                except ImportError:
                    logger.warning("Google AI packages not installed. Install: pip install google-genai")
                    return self._generate_mock_images(prompt, count, style, aspect_ratio)
            
        except Exception as e:
            logger.error(f"Gemini image generation error: {e}")
            return self._generate_mock_images(prompt, count, style, aspect_ratio)
    
    def _generate_with_dalle(self, prompt: str, count: int, style: str, aspect_ratio: str, reference_image_url: Optional[str] = None, reference_image_base64: Optional[str] = None) -> list[dict[str, Any]]:
        """Generate images using OpenAI DALL-E API."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            # DALL-E 3 doesn't support direct image input, so enhance prompt with reference description
            if reference_image_url or reference_image_base64:
                enhanced_prompt = f"Create an improved version of this product design: {prompt}. Style: {style}, aspect ratio: {aspect_ratio}. Make it better, more professional, and appealing. High quality product image."
            else:
                enhanced_prompt = f"{prompt}, {style} style, aspect ratio {aspect_ratio}, high quality product image"
            
            images = []
            
            for i in range(count):
                try:
                    # Note: DALL-E 3 doesn't support image-to-image directly, but we can describe improvements
                    variant_prompt = f"{enhanced_prompt} Variation {i+1}: more unique and eye-catching"
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=variant_prompt,
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    images.append({
                        "url": response.data[0].url,
                        "prompt": enhanced_prompt,
                        "style": style,
                        "aspect_ratio": aspect_ratio
                    })
                except Exception as e:
                    logger.warning(f"DALL-E image {i+1} generation failed: {e}")
                    continue
            
            return images
            
        except ImportError:
            logger.warning("openai not installed. Using mock images.")
            return self._generate_mock_images(prompt, count, style, aspect_ratio)
        except Exception as e:
            logger.error(f"DALL-E generation error: {e}")
            return self._generate_mock_images(prompt, count, style, aspect_ratio)
    
    def _generate_with_stability(self, prompt: str, count: int, style: str, aspect_ratio: str, reference_image_url: Optional[str] = None, reference_image_base64: Optional[str] = None) -> list[dict[str, Any]]:
        """Generate images using Stability AI API."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            # Stability AI supports image-to-image via init_image parameter
            if reference_image_base64:
                enhanced_prompt = f"Improve this design: {prompt}. Style: {style}, make it better and more professional"
            elif reference_image_url:
                enhanced_prompt = f"Improve this design: {prompt}. Style: {style}, make it better and more professional"
                # Download reference image
                try:
                    img_resp = requests.get(reference_image_url, timeout=10)
                    if img_resp.status_code == 200:
                        reference_image_base64 = base64.b64encode(img_resp.content).decode()
                except:
                    pass
            else:
                enhanced_prompt = f"{prompt}, {style} style, aspect ratio {aspect_ratio}, high quality product image"
            
            images = []
            for i in range(count):
                try:
                    files = {}
                    data = {
                        "prompt": f"{enhanced_prompt}, variation {i+1}",
                        "output_format": "png"
                    }
                    
                    # Add init_image if we have reference
                    if reference_image_base64:
                        import io
                        img_bytes = base64.b64decode(reference_image_base64)
                        files["init_image"] = ("image.png", img_bytes, "image/png")
                        data["image_strength"] = 0.35  # Blend factor
                    
                    response = requests.post(
                        "https://api.stability.ai/v2beta/stable-image/generate/core",
                        headers=headers,
                        files=files if files else {"none": ""},
                        data=data,
                        timeout=30
                    )
                    if response.status_code == 200:
                        images.append({
                            "url": None,
                            "base64": base64.b64encode(response.content).decode(),
                            "prompt": enhanced_prompt,
                            "style": style,
                            "aspect_ratio": aspect_ratio
                        })
                except Exception as e:
                    logger.warning(f"Stability AI image {i+1} generation failed: {e}")
                    continue
            
            return images
            
        except Exception as e:
            logger.error(f"Stability AI generation error: {e}")
            return self._generate_mock_images(prompt, count, style, aspect_ratio)
    
    def _generate_mock_images(self, prompt: str, count: int, style: str, aspect_ratio: str) -> list[dict[str, Any]]:
        """Generate mock placeholder images."""
        return [
            {
                "url": f"https://via.placeholder.com/800x800/4a90e2/ffffff?text={prompt[:30].replace(' ', '+')}+{i+1}",
                "prompt": prompt,
                "style": style,
                "aspect_ratio": aspect_ratio,
                "mock": True
            }
            for i in range(count)
        ]

