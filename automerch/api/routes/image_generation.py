"""Image generation API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
import time

from ...services.image_generator.client import ImageGenerator
from ...services.image_generator.utils import save_image_from_base64, download_image_from_url
from pathlib import Path

router = APIRouter(prefix="/api/images", tags=["images"])


class GenerateImageRequest(BaseModel):
    """Request to generate product images."""
    prompt: str
    count: int = 5
    style: str = "professional"
    aspect_ratio: str = "1:1"
    research_data: Optional[dict[str, Any]] = None  # Optional research insights to enhance prompt
    reference_image_url: Optional[str] = None  # URL of reference image to improve upon
    reference_image_base64: Optional[str] = None  # Base64 encoded reference image


@router.post("/generate")
def generate_images(request: GenerateImageRequest):
    """Generate product images based on a prompt and optional research data.
    
    Args:
        request: Image generation request with prompt and options
        
    Returns:
        List of generated images
    """
    try:
        generator = ImageGenerator()
        
        # Enhance prompt with research data if provided
        enhanced_prompt = request.prompt
        if request.research_data:
            metrics = request.research_data.get("metrics", {})
            llm = request.research_data.get("llm", {})
            
            # Add research insights to prompt
            enhancements = []
            if metrics.get("competition_score"):
                enhancements.append(f"optimized for market with competition score {metrics['competition_score']}")
            if llm.get("recommended_tags"):
                tags = llm["recommended_tags"]
                if isinstance(tags, list):
                    enhancements.append(f"tags: {', '.join(tags[:5])}")
                elif isinstance(tags, str):
                    enhancements.append(f"tags: {tags}")
            if llm.get("design_blueprints"):
                blueprints = llm["design_blueprints"]
                if blueprints and isinstance(blueprints, list) and len(blueprints) > 0:
                    bp = blueprints[0]
                    if isinstance(bp, dict):
                        enhancements.append(f"style: {bp.get('style', '')}")
                        if bp.get("colors"):
                            colors = bp["colors"]
                            if isinstance(colors, list):
                                enhancements.append(f"colors: {', '.join(colors[:3])}")
                            elif isinstance(colors, str):
                                enhancements.append(f"colors: {colors}")
            
            if enhancements:
                enhanced_prompt = f"{enhanced_prompt}, {'; '.join(enhancements)}"
        
        # Save reference image locally if provided
        reference_image_path = None
        if request.reference_image_base64:
            images_dir = Path("generated_images") / "references"
            reference_image_path = save_image_from_base64(
                request.reference_image_base64,
                images_dir,
                f"ref_{int(time.time())}"
            )
        elif request.reference_image_url:
            images_dir = Path("generated_images") / "references"
            reference_image_path = download_image_from_url(
                request.reference_image_url,
                images_dir,
                f"ref_{int(time.time())}"
            )
        
        images = generator.generate_product_images(
            prompt=enhanced_prompt,
            count=request.count,
            style=request.style,
            aspect_ratio=request.aspect_ratio,
            reference_image_url=request.reference_image_url,
            reference_image_base64=request.reference_image_base64
        )
        
        # Save generated images locally
        generated_image_paths = []
        output_dir = Path("generated_images") / "products"
        for idx, img in enumerate(images):
            if img.get("base64"):
                saved_path = save_image_from_base64(
                    img["base64"],
                    output_dir,
                    f"generated_{int(time.time())}_{idx}"
                )
                if saved_path:
                    generated_image_paths.append(str(saved_path))
            elif img.get("url"):
                # Download generated image if it's a URL
                saved_path = download_image_from_url(
                    img["url"],
                    output_dir,
                    f"generated_{int(time.time())}_{idx}"
                )
                if saved_path:
                    generated_image_paths.append(str(saved_path))
        
        return {
            "images": images,
            "count": len(images),
            "prompt": enhanced_prompt,
            "original_prompt": request.prompt,
            "reference_image_path": str(reference_image_path) if reference_image_path else None,
            "generated_image_paths": generated_image_paths
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.post("/generate-from-research")
def generate_from_research(
    keywords: str,
    research_data: dict[str, Any],
    count: int = 5,
    style: str = "professional"
):
    """Generate product images directly from research results.
    
    Args:
        keywords: Research keywords
        research_data: Full research results from /api/research
        count: Number of images to generate
        style: Image style
        
    Returns:
        Generated images
    """
    try:
        # Build prompt from research data
        llm = research_data.get("llm", {})
        metrics = research_data.get("metrics", {})
        
        # Create prompt from design blueprints if available
        if llm.get("design_blueprints") and isinstance(llm["design_blueprints"], list) and len(llm["design_blueprints"]) > 0:
            blueprint = llm["design_blueprints"][0]
            if isinstance(blueprint, dict):
                prompt_parts = [keywords]
                if blueprint.get("on_art_text"):
                    prompt_parts.append(f"with text: '{blueprint['on_art_text']}'")
                if blueprint.get("visuals"):
                    visuals = blueprint["visuals"]
                    if isinstance(visuals, list):
                        prompt_parts.append(f"visuals: {', '.join(visuals[:3])}")
                    elif isinstance(visuals, str):
                        prompt_parts.append(f"visuals: {visuals}")
                if blueprint.get("style"):
                    prompt_parts.append(f"in {blueprint['style']} style")
                prompt = ", ".join(prompt_parts)
            else:
                prompt = keywords
        else:
            # Fallback to keywords with market insights
            prompt = f"{keywords} product design"
        
        generator = ImageGenerator()
        images = generator.generate_product_images(
            prompt=prompt,
            count=count,
            style=style,
            aspect_ratio="1:1"
        )
        
        return {
            "images": images,
            "count": len(images),
            "prompt": prompt,
            "keywords": keywords,
            "research_based": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research-based image generation failed: {str(e)}")

