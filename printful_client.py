import os

dry_run = os.getenv("AUTOMERCH_DRY_RUN", "true").lower() == "true"
PRINTFUL_API_KEY = os.getenv("PRINTFUL_API_KEY")

def create_product(product):
    if dry_run:
        return 'VARIANT-DRYRUN', ['https://example.com/hero.png']
    # TODO: real API call to Printful
    return 'VARIANT123', ['https://example.com/hero.png']


def get_store_metrics():
    # Placeholder metrics
    return {"orders": 0, "revenue": 0.0}
