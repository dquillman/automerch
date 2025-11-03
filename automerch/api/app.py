"""Main FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback

from .routes import auth, drafts, assets, ui, pages, research, products, image_generation, shops
from ..core.db import init_db

# Initialize database on import
try:
    init_db()
except Exception as e:
    print(f"Warning: Database initialization had issues: {e}")

app = FastAPI(
    title="AutoMerch Lite",
    description="Etsy drafts automation tool",
    version="1.0.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(drafts.router)
app.include_router(assets.router)
app.include_router(ui.router)
app.include_router(pages.router)
app.include_router(research.router)
app.include_router(products.router)
app.include_router(image_generation.router)
app.include_router(shops.router)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"ok": True, "status": "healthy"}


@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    try:
        init_db()
    except Exception as e:
            print(f"Warning: Database init in startup had issues: {e}")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Better validation error messages."""
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(x) for x in error["loc"])
        errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error - check the fields below",
            "errors": errors,
            "tip": "Make sure all required fields (sku, title, description, price) are provided with correct types"
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to provide better error messages."""
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": str(request.url.path),
        "traceback": traceback.format_exc()
    }
    # Print to console for debugging
    print(f"\n❌ Error on {request.url.path}:")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": str(request.url.path),
            "tip": "Check server logs for full traceback"
        }
    )

