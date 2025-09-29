import typer
from typing import Optional
from db import get_session, init_db
from models import Product
from version import get_version

app = typer.Typer(help="AutoMerch management CLI")


@app.command()
def version():
    """Print app version."""
    typer.echo(get_version())


@app.command()
def seed(clear: bool = typer.Option(False, help="Wipe existing products before seeding")):
    """Seed demo products for preview."""
    init_db()
    demo = [
        {"sku": "TEE-CLASSIC-BLK-M", "name": "Classic Tee (Black, M)", "price": 19.99, "quantity": 25, "variant_id": 4011, "thumbnail_url": "https://picsum.photos/seed/tee1/256/256"},
        {"sku": "TEE-CLASSIC-WHT-L", "name": "Classic Tee (White, L)", "price": 21.99, "quantity": 30, "variant_id": 4012, "thumbnail_url": "https://picsum.photos/seed/tee2/256/256"},
        {"sku": "MUG-11OZ-LOGO", "name": "Logo Mug 11oz", "price": 14.99, "quantity": 50, "variant_id": 4013, "thumbnail_url": "https://picsum.photos/seed/mug1/256/256"},
    ]
    with get_session() as s:
        if clear:
            for p in s.exec(Product.select()).all() if hasattr(Product, 'select') else s.query(Product).all():
                s.delete(p)
            s.commit()
        for d in demo:
            p = s.get(Product, d["sku"]) or Product(sku=d["sku"])  # type: ignore
            for k, v in d.items():
                setattr(p, k, v)
            s.add(p)
        s.commit()
    typer.echo("Seeded demo products.")


if __name__ == "__main__":
    app()
