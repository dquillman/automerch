from db import get_session
from models import Product, RunLog


def run(dry_run: bool = True):
    """Placeholder: reconcile local quantities with marketplace.

    If you later store Printful/warehouse stock, compare and update Product.quantity
    and optionally pause listings when out of stock.
    """
    examined = 0
    updated = 0
    with get_session() as s:
        rows = s.query(Product).all()
        for p in rows:
            examined += 1
            # Without external inventory source, we just ensure quantity is set for active products
            if p.quantity is None:
                if dry_run:
                    updated += 1
                    continue
                p.quantity = 999
                s.add(p)
                s.commit()
                updated += 1
    with get_session() as s:
        s.add(RunLog(job="sync_inventory", status="ok", message=f"examined={examined}, updated={updated}, dry_run={dry_run}"))
        s.commit()

