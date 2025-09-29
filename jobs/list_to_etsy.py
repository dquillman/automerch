from models import Product
from db import get_session
from etsy_client import create_listing_draft

def run():
    # Example: take first product and create a draft listing
    with get_session() as s:
        prod = s.query(Product).first()
    sku = prod.sku if prod else 'DEMO-SKU'
    listing_id = create_listing_draft({'sku': sku})
    print(f"Created Etsy draft listing {listing_id} for {sku}")
