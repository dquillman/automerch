"""UI routes for serving HTML pages."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["ui"])

# Templates directory - look for UI templates
# Path: automerch_remote/automerch/api/routes/ui.py
#      -> api/routes -> api -> automerch -> automerch_remote
ui_file_path = Path(__file__).absolute()
# Go up 4 levels: routes -> api -> automerch -> automerch_remote
base_dir = ui_file_path.parent.parent.parent.parent
# Target: automerch_remote/automerch/ui/drafts_queue
templates_dir = base_dir / "automerch" / "ui" / "drafts_queue"

# If that doesn't exist, try alternative
if not templates_dir.exists():
    # Try relative to automerch package
    automerch_dir = ui_file_path.parent.parent.parent
    templates_dir = automerch_dir / "ui" / "drafts_queue"

templates = Jinja2Templates(directory=str(templates_dir)) if templates_dir.exists() else None


@router.get("/workflow", response_class=HTMLResponse)
def workflow_page(request: Request):
    """Render workflow guide page."""
    try:
        # Find workflow template - try multiple paths
        ui_dir = templates_dir.parent if templates_dir and templates_dir.exists() else None
        if not ui_dir:
            # Try alternative path
            automerch_dir = ui_file_path.parent.parent.parent
            ui_dir = automerch_dir / "ui"
        
        workflow_path = ui_dir / "workflow" / "workflow.html"
        
        if workflow_path.exists():
            # Read and return the HTML file directly
            with open(workflow_path, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        
        # Fallback
        return HTMLResponse(f"""
        <html>
            <head><title>Workflow</title></head>
            <body>
                <h1>Workflow Guide</h1>
                <p>Workflow template not found at: {workflow_path}</p>
                <p>See API documentation at <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(f"""
        <html>
            <head><title>Error</title></head>
            <body>
                <h1>Error Loading Workflow Page</h1>
                <p>Error: {str(e)}</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """, status_code=500)


@router.get("/drafts/create", response_class=HTMLResponse)
def create_draft_page(request: Request):
    """Draft creation form page."""
    create_path = ui_dir / "drafts" / "create.html"
    if create_path.exists():
        with open(create_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Create Draft</h1><p>Page not found</p>")


@router.get("/drafts", response_class=HTMLResponse)
def drafts_queue(request: Request):
    """Render drafts queue page."""
    try:
        # Try enhanced version first if templates are loaded
        if templates and templates_dir and templates_dir.exists():
            enhanced_path = templates_dir / "enhanced_queue.html"
            if enhanced_path.exists():
                return templates.TemplateResponse("enhanced_queue.html", {"request": request})
            
            # Fallback to basic queue.html
            queue_path = templates_dir / "queue.html"
            if queue_path.exists():
                return templates.TemplateResponse("queue.html", {"request": request})
        
        # Return simple HTML if templates not found
        return HTMLResponse("""
        <html>
            <head><title>Drafts Queue</title></head>
            <body>
                <h1>Drafts Queue</h1>
                <p>Templates directory not found. Using API endpoint instead:</p>
                <p><a href="/api/drafts/queue">View Drafts (JSON)</a></p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(f"""
        <html>
            <head><title>Error</title></head>
            <body>
                <h1>Error Loading Page</h1>
                <p>Error: {str(e)}</p>
                <p><a href="/api/drafts/queue">View Drafts (JSON)</a></p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """, status_code=500)

