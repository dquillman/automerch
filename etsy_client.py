import os

dry_run = os.getenv("AUTOMERCH_DRY_RUN", "true").lower() == "true"
ETSY_ACCESS_TOKEN = os.getenv("ETSY_ACCESS_TOKEN")
ETSY_SHOP_ID = os.getenv("ETSY_SHOP_ID")

def create_listing_draft(product):
    if dry_run:
        return 'LISTING-DRYRUN'
    # TODO: real API call using Etsy Open API
    # placeholder behavior
    return 'LISTING123'
