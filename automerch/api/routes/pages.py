"""Additional UI pages for the complete app."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter(tags=["pages"])

# Find UI directory
ui_file_path = Path(__file__).absolute()
automerch_dir = ui_file_path.parent.parent.parent
ui_dir = automerch_dir / "ui"


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """Main dashboard page."""
    dashboard_path = ui_dir / "dashboard" / "dashboard.html"
    if dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Dashboard</h1><p>Dashboard not found</p>")


@router.get("/research", response_class=HTMLResponse)
def research_page(request: Request):
    """Research page."""
    research_path = ui_dir / "research" / "research.html"
    if research_path.exists():
        with open(research_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Research</h1><p>Research page not found</p>")


@router.get("/research/detail", response_class=HTMLResponse)
def research_detail_page(request: Request):
    """Research detail page with full data and image generation."""
    detail_path = ui_dir / "research" / "detail.html"
    if detail_path.exists():
        with open(detail_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Research Details</h1><p>Detail page not found</p>")


@router.get("/products/create", response_class=HTMLResponse)
def create_product_page(request: Request):
    """Product creation page."""
    product_path = ui_dir / "products" / "create.html"
    if product_path.exists():
        with open(product_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Create Product</h1><p>Page not found</p>")


@router.get("/products/printful", response_class=HTMLResponse)
def printful_page(request: Request):
    """Printful integration page."""
    printful_path = ui_dir / "products" / "printful.html"
    if printful_path.exists():
        with open(printful_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Printful</h1><p>Page not found</p>")


@router.get("/assets", response_class=HTMLResponse)
def assets_page(request: Request):
    """Assets management page."""
    assets_path = ui_dir / "assets" / "assets.html"
    if assets_path.exists():
        with open(assets_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Assets</h1><p>Page not found</p>")


@router.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request):
    """Analytics dashboard."""
    analytics_path = ui_dir / "analytics" / "analytics.html"
    if analytics_path.exists():
        with open(analytics_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Analytics</h1><p>Page not found</p>")


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    """Settings page."""
    settings_path = ui_dir / "settings" / "settings.html"
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Settings</h1><p>Page not found</p>")

