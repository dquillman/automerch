from db import get_session
from models import Product, RunLog


def _round_99(value: float) -> float:
    return round(max(0.0, float(value)) + 0.001, 2) if value is not None else value


def run(dry_run: bool = True):
    """Apply a simple pricing rule: ensure .99 ending if price is set.

    In dry_run, just logs proposed changes. When not dry_run, updates DB and Etsy listing price if present.
    """
    from etsy_client import update_listing_price
    changed = 0
    examined = 0
    errors = 0
    with get_session() as s:
        rows = s.query(Product).all()
        for p in rows:
            examined += 1
            if p.price is None:
                continue
            target = _round_99(p.price)
            if abs((p.price or 0) - target) >= 0.01:
                if dry_run:
                    changed += 1
                    continue
                try:
                    p.price = target
                    s.add(p)
                    s.commit()
                    if p.etsy_listing_id:
                        update_listing_price(p.etsy_listing_id, float(target))
                    changed += 1
                except Exception:
                    errors += 1
                    s.rollback()
    with get_session() as s:
        s.add(RunLog(job="sync_prices", status="ok", message=f"examined={examined}, changed={changed}, errors={errors}, dry_run={dry_run}"))
        s.commit()

