# Migration Guide: Integrating AutoMerch Lite with Existing App

## Overview

This guide shows how to integrate the new `automerch/` package structure with your existing `app.py`.

## Option 1: Keep Both Apps Separate (Recommended for Testing)

Run the new API alongside your existing app on a different port:

```bash
# Existing app (port 8000)
uvicorn app:app --reload --port 8000

# New AutoMerch Lite API (port 8001)
uvicorn automerch.api.app:app --reload --port 8001
```

## Option 2: Merge into Existing App

Add the new routes to your existing `app.py`:

```python
# At the top of app.py, add:
from automerch.api.routes import auth, drafts, assets
from automerch.api.dependencies import get_etsy_client

# Include the new routers
app.include_router(auth.router)
app.include_router(drafts.router)
app.include_router(assets.router)
```

## Option 3: Gradual Migration

Use the new services in your existing routes:

```python
# In your existing product_to_etsy route:
from automerch.services.etsy.drafts import EtsyDraftsService
from automerch.api.dependencies import get_etsy_client

@app.post("/api/products/etsy")
def product_to_etsy(sku: str = Form(...)):
    client = get_etsy_client()
    service = EtsyDraftsService(client)
    
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj is None:
            return RedirectResponse(url="/products", status_code=303)
        
        result = service.create_draft(
            title=obj.name or obj.sku,
            description=obj.description or "",
            price=obj.price or 19.99,
            images=[obj.thumbnail_url] if obj.thumbnail_url else None
        )
        
        obj.etsy_listing_id = result["listing_id"]
        session.add(obj)
        session.commit()
    
    return RedirectResponse(url="/products", status_code=303)
```

## Testing the Integration

1. **Test OAuth:**
   ```bash
   # Visit: http://localhost:8000/auth/etsy/login
   ```

2. **Test Draft Creation:**
   ```python
   from automerch.services.etsy.drafts import EtsyDraftsService
   
   service = EtsyDraftsService()
   result = service.create_draft(
       title="Test Product",
       description="Test description",
       price=19.99
   )
   print(result)
   ```

3. **Test API Endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/drafts/new \
     -H "Content-Type: application/json" \
     -d '{"sku": "TEST-001", "title": "Test", "description": "Test", "price": 19.99}'
   ```

## Troubleshooting

- **Import errors:** Make sure you're running from `automerch_remote/` directory
- **Database issues:** Run `init_db()` to create new tables
- **OAuth not working:** Check `.env` has correct `ETSY_CLIENT_ID` and `ETSY_CLIENT_SECRET`





