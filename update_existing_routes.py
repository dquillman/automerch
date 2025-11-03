"""Update existing routes in app.py to use new AutoMerch Lite services.

This creates updated versions of existing product-to-etsy routes using the new service layer.
"""

def get_updated_product_to_etsy_route():
    """Return updated route code that uses new services."""
    return '''
@app.post("/api/products/etsy_v2")
def product_to_etsy_v2(sku: str = Form(...)):
    """Create Etsy draft using new AutoMerch Lite service layer."""
    try:
        from automerch.services.etsy.drafts import EtsyDraftsService
        from automerch.api.dependencies import get_etsy_client
        
        with get_session() as session:
            obj = session.get(Product, sku)
            if obj is None:
                return RedirectResponse(url="/products", status_code=303)
            
            # Get authenticated client
            client = get_etsy_client()
            service = EtsyDraftsService(client)
            
            # Create draft
            result = service.create_draft(
                title=obj.name or obj.sku,
                description=(obj.description or "")[:45000],
                price=obj.price or 19.99,
                taxonomy_id=getattr(obj, 'taxonomy_id', None) or 6947,
                tags=(obj.tags.split(",") if hasattr(obj, 'tags') and obj.tags else []),
                images=[obj.thumbnail_url] if obj.thumbnail_url else None
            )
            
            # Store listing ID
            obj.etsy_listing_id = result["listing_id"]
            session.add(obj)
            
            # Create Listing record
            from automerch.models import Listing
            listing = Listing(
                listing_id=result["listing_id"],
                etsy_listing_id=result["listing_id"],
                sku=obj.sku,
                title=obj.name or obj.sku,
                price=obj.price or 19.99,
                status="draft",
                etsy_url=result.get("etsy_url")
            )
            session.add(listing)
            
            session.commit()
            
            session.add(RunLog(
                job="etsy_list_v2",
                status="ok",
                message=f"Draft created: {result['listing_id']}"
            ))
            session.commit()
            
    except Exception as e:
        with get_session() as session:
            session.add(RunLog(
                job="etsy_list_v2",
                status="error",
                message=str(e)
            ))
            session.commit()
    
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/bulk/etsy_draft_v2")
def bulk_etsy_draft_v2(skus: list[str] = Form(default_factory=list)):
    """Bulk create drafts using new service layer."""
    from automerch.services.etsy.drafts import EtsyDraftsService
    from automerch.api.dependencies import get_etsy_client
    
    created = 0
    skipped = 0
    errors = 0
    
    try:
        client = get_etsy_client()
        service = EtsyDraftsService(client)
    except Exception as e:
        with get_session() as session:
            session.add(RunLog(
                job="bulk_etsy_draft_v2",
                status="error",
                message=f"Failed to get client: {e}"
            ))
            session.commit()
        return RedirectResponse(url="/products", status_code=303)
    
    with get_session() as session:
        for sku in skus or []:
            obj = session.get(Product, sku)
            if not obj:
                skipped += 1
                continue
            if obj.etsy_listing_id:
                skipped += 1
                continue
            
            try:
                result = service.create_draft(
                    title=obj.name or obj.sku,
                    description=(obj.description or "")[:45000],
                    price=obj.price or 19.99,
                    taxonomy_id=getattr(obj, 'taxonomy_id', None) or 6947,
                    tags=(obj.tags.split(",") if hasattr(obj, 'tags') and obj.tags else []),
                    images=[obj.thumbnail_url] if obj.thumbnail_url else None
                )
                
                obj.etsy_listing_id = result["listing_id"]
                session.add(obj)
                
                from automerch.models import Listing
                listing = Listing(
                    listing_id=result["listing_id"],
                    etsy_listing_id=result["listing_id"],
                    sku=obj.sku,
                    title=obj.name or obj.sku,
                    price=obj.price or 19.99,
                    status="draft",
                    etsy_url=result.get("etsy_url")
                )
                session.add(listing)
                session.commit()
                created += 1
            except Exception as e:
                errors += 1
                session.add(RunLog(
                    job="bulk_etsy_draft_v2",
                    status="error",
                    message=f"{sku}: {e}"
                ))
                session.commit()
        
        session.add(RunLog(
            job="bulk_etsy_draft_v2",
            status="ok",
            message=f"{created} created, {skipped} skipped, {errors} errors"
        ))
        session.commit()
    
    return RedirectResponse(url="/products", status_code=303)
'''


