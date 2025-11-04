"""Product management routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel

from ...core.db import get_session
from ...models import Product
from ...api.dependencies import PrintfulClientDep

router = APIRouter(prefix="/api/products", tags=["products"])


class ProductRequest(BaseModel):
    """Product creation request."""
    sku: str
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    taxonomy_id: Optional[int] = None
    tags: Optional[str] = None
    thumbnail_url: Optional[str] = None


@router.post("")
def create_product(product: ProductRequest):
    """Create or update a product.
    
    Args:
        product: Product data from request body
        
    Returns:
        Created/updated product
    """
    try:
        with next(get_session()) as session:
            db_product = session.get(Product, product.sku) or Product(sku=product.sku)
            
            if product.name:
                db_product.name = product.name
            if product.description:
                db_product.description = product.description
            if product.price:
                db_product.price = product.price
            if product.cost:
                db_product.cost = product.cost
            if product.taxonomy_id:
                db_product.taxonomy_id = product.taxonomy_id
            if product.tags:
                db_product.tags = product.tags
            if product.thumbnail_url:
                db_product.thumbnail_url = product.thumbnail_url
            
            session.add(db_product)
            session.commit()
            session.refresh(db_product)
            
            return {
                "sku": db_product.sku,
                "name": db_product.name,
                "price": db_product.price,
                "status": "created" if not db_product.created_at else "updated"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")


@router.get("")
def list_products(skip: int = 0, limit: int = 100):
    """List all products.
    
    Args:
        skip: Number of products to skip
        limit: Maximum number of products to return
        
    Returns:
        List of products
    """
    try:
        with next(get_session()) as session:
            from sqlmodel import select
            stmt = select(Product).offset(skip).limit(limit).order_by(Product.created_at.desc())
            products = session.exec(stmt).all()
            
            return [
                {
                    "sku": p.sku,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "cost": p.cost,
                    "taxonomy_id": p.taxonomy_id,
                    "tags": p.tags,
                    "thumbnail_url": p.thumbnail_url,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in products
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list products: {str(e)}")


@router.get("/{sku}")
def get_product(sku: str):
    """Get product by SKU.
    
    Args:
        sku: Product SKU
        
    Returns:
        Product details
    """
    try:
        with next(get_session()) as session:
            product = session.get(Product, sku)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            return {
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "cost": product.cost,
                "taxonomy_id": product.taxonomy_id,
                "tags": product.tags,
                "thumbnail_url": product.thumbnail_url,
                "etsy_listing_id": product.etsy_listing_id,
                "created_at": product.created_at.isoformat() if product.created_at else None
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get product: {str(e)}")


class PrintfulProductRequest(BaseModel):
    """Printful product creation request."""
    sku: str
    name: str
    price: float
    thumbnail: str
    variant_id: int = 4011


@router.post("/printful")
def create_printful_product(
    req: PrintfulProductRequest,
    printful_client: PrintfulClientDep
):
    """Create a Printful product.
    
    Args:
        req: Printful product data from request body
        printful_client: Injected PrintfulClient dependency
        
    Returns:
        Created product info
    """
    try:
        # Create product in database first
        with next(get_session()) as session:
            product = session.get(Product, req.sku) or Product(sku=req.sku, name=req.name)
            
            product.price = req.price
            product.variant_id = req.variant_id or 4011  # Default to mug
            product.thumbnail_url = req.thumbnail
            
            session.add(product)
            session.commit()
            session.refresh(product)
        
        # Create product in Printful
        printful_result = printful_client.create_product(
            name=req.name,
            thumbnail=req.thumbnail,
            sku=req.sku,
            variant_id=req.variant_id,
            retail_price=req.price,
            design_url=req.thumbnail  # Use thumbnail as design
        )
        
        # Update product with Printful variant ID if available
        if printful_result.get("variant_id"):
            with next(get_session()) as session:
                product = session.get(Product, req.sku)
                if product:
                    product.printful_variant_id = printful_result.get("variant_id")
                    session.add(product)
                    session.commit()
        
        return {
            "sku": product.sku,
            "name": product.name,
            "variant_id": req.variant_id,
            "printful_variant_id": printful_result.get("variant_id"),
            "printful_product_id": printful_result.get("product_id"),
            "status": "created",
            "printful_status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Printful product: {str(e)}")


@router.get("/printful")
def list_printful_products(
    limit: int = 20,
    offset: int = 0,
    printful_client: PrintfulClientDep = None
):
    """List all Printful products in your store.
    
    Args:
        limit: Maximum number of products to return
        offset: Number of products to skip
        printful_client: Injected PrintfulClient dependency
        
    Returns:
        List of Printful products with pagination info
    """
    try:
        if printful_client is None:
            from ...api.dependencies import get_printful_client
            printful_client = get_printful_client()
        
        result = printful_client.list_products(limit=limit, offset=offset)
        
        return {
            "products": result.get("products", []),
            "total": result.get("total", 0),
            "limit": result.get("limit", limit),
            "offset": result.get("offset", offset)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list Printful products: {str(e)}")


@router.get("/printful/{product_id}")
def get_printful_product(
    product_id: int,
    printful_client: PrintfulClientDep = None
):
    """Get Printful product details by ID.
    
    Args:
        product_id: Printful sync product ID
        printful_client: Injected PrintfulClient dependency
        
    Returns:
        Printful product details
    """
    try:
        if printful_client is None:
            from ...api.dependencies import get_printful_client
            printful_client = get_printful_client()
        
        product = printful_client.get_product(product_id)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Printful product: {str(e)}")


@router.get("/printful/integration")
def get_printful_integration():
    """Get integration status - which local products are synced to Printful.
    
    Returns:
        List of local products with their Printful sync status
    """
    try:
        with next(get_session()) as session:
            from sqlmodel import select
            # Get all products that have Printful variant IDs
            stmt = select(Product).where(Product.printful_variant_id.isnot(None))
            synced_products = session.exec(stmt).all()
            
            # Get all products for comparison
            all_products = session.exec(select(Product)).all()
            
            synced = [
                {
                    "sku": p.sku,
                    "name": p.name,
                    "price": p.price,
                    "printful_variant_id": p.printful_variant_id,
                    "thumbnail_url": p.thumbnail_url,
                    "sync_status": "synced"
                }
                for p in synced_products
            ]
            
            not_synced = [
                {
                    "sku": p.sku,
                    "name": p.name,
                    "price": p.price,
                    "thumbnail_url": p.thumbnail_url,
                    "sync_status": "not_synced"
                }
                for p in all_products
                if p.printful_variant_id is None
            ]
            
            return {
                "synced": synced,
                "not_synced": not_synced,
                "total_synced": len(synced),
                "total_not_synced": len(not_synced),
                "total_products": len(all_products)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")


