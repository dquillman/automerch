"""Research API routes."""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import sys
from pathlib import Path
import traceback

router = APIRouter(prefix="/api/research", tags=["research"])

# Add parent directory to path for research.py
# The research.py file is in automerch_remote/, same level as automerch/
current_file = Path(__file__).absolute()
automerch_remote_dir = current_file.parent.parent.parent.parent
sys.path.insert(0, str(automerch_remote_dir))

from fastapi.responses import FileResponse


@router.get("")
def research_api(q: str = Query(..., description="Search keywords"), limit: int = Query(50, ge=10, le=200)):
    """Run product research.
    
    Args:
        q: Search keywords
        limit: Number of listings to analyze (10-200)
        
    Returns:
        Research results with metrics and insights
    """
    try:
        # Import research function from existing codebase
        # The old models.py now uses extend_existing=True to avoid conflicts
        from research import run_research
        result = run_research(q, limit=limit)
        return result
    except ImportError as e:
        # More detailed error message
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=501,
            detail=f"Research module not found. Error: {str(e)}\nTraceback: {tb}"
        )
    except Exception as e:
        # Include full traceback for debugging
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Research failed: {str(e)}\nTraceback: {tb}"
        )


@router.get("/image/{filename}")
def get_research_image(filename: str):
    """Serve research images from local storage."""
    current_file = Path(__file__).absolute()
    automerch_remote_dir = current_file.parent.parent.parent.parent
    image_path = automerch_remote_dir / "research_images" / filename
    
    if image_path.exists() and image_path.is_file():
        return FileResponse(
            path=str(image_path),
            media_type="image/jpeg"
        )
    raise HTTPException(status_code=404, detail="Image not found")

