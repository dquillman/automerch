import importlib
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import select

from db import init_db, get_session
from models import Product, RunLog, ResearchSnapshot
from version import get_version
from research import run_research

BASE_DIR = Path(__file__).parent
MEDIA_DIR = BASE_DIR / "media"
MEDIA_PRODUCTS = MEDIA_DIR / "products"
MEDIA_PRODUCTS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AutoMerch")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
templates = Jinja2Templates(directory="templates")
templates.env.globals["APP_VERSION"] = get_version()
scheduler = BackgroundScheduler()


@app.on_event("startup")
def on_startup():
    init_db()
    scheduler.start()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Home"})


@app.get("/products")
def products_page(request: Request):
    with get_session() as session:
        products = session.exec(select(Product)).all()
    printful_variants = [
        {"id": 4011, "label": "4011 - Tee (example)"},
        {"id": 4012, "label": "4012 - Tee (example)"},
        {"id": 4013, "label": "4013 - Tee (example)"},
    ]
    return templates.TemplateResponse(
        "products.html",
        {"request": request, "products": products, "title": "Products", "printful_variants": printful_variants},
    )


@app.post("/api/products")
def add_product(
    sku: str = Form(...),
    name: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    variant_id: Optional[str] = Form(None),
    thumbnail_url: Optional[str] = Form(None),
):
    with get_session() as session:
        obj = session.get(Product, sku) or Product(sku=sku)
        if name:
            obj.name = name
        if price:
            try:
                obj.price = float(price)
            except ValueError:
                pass
        if description:
            obj.description = description
        if variant_id:
            try:
                obj.variant_id = int(variant_id)
            except ValueError:
                pass
        if thumbnail_url:
            obj.thumbnail_url = thumbnail_url
        session.add(obj)
        session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.get("/research")
def research_page(request: Request, q: str | None = None, limit: int = 50):
    data = None
    err = None
    if q:
        try:
            data = run_research(q, limit=limit)
        except Exception as e:
            err = str(e)
    return templates.TemplateResponse(
        "research.html",
        {"request": request, "title": "Research", "q": q or "", "limit": limit, "data": data, "err": err},
    )


@app.get("/api/research")
def research_api(q: str, limit: int = 50):
    return run_research(q, limit=limit)


def _slugify(value: str) -> str:
    value = (value or "").lower()
    keep = []
    for ch in value:
        if ch.isalnum():
            keep.append(ch)
        elif ch in [' ', '-', '_']:
            keep.append('-')
        else:
            keep.append('')
    slug = ''.join(keep)
    while '--' in slug:
        slug = slug.replace('--', '-')
    slug = slug.strip('-')
    return slug or 'design'


@app.post("/api/research/import_blueprints")
def import_blueprints(
    q: str = Form(...),
    limit: int = Form(50),
    price_override: str | None = Form(None),
    blueprints_json: str = Form(...),
    idx: list[str] = Form(default_factory=list),
):
    import json
    from uuid import uuid4

    try:
        blueprints = json.loads(blueprints_json) if blueprints_json else []
    except Exception:
        blueprints = []
    selected = []
    for s in idx:
        try:
            i = int(s)
            if 0 <= i < len(blueprints):
                selected.append((i, blueprints[i]))
        except Exception:
            continue
    # Determine price to set
    price_val = None
    if price_override:
        try:
            price_val = float(price_override)
        except ValueError:
            price_val = None

    created = 0
    with get_session() as session:
        for i, bp in selected:
            name = str(bp.get("name") or bp.get("on_art_text") or f"{q} design {i}").strip()
            sku_base = _slugify(f"{q}-{name}")[:40]
            # ensure uniqueness by suffix
            sku = sku_base
            suffix_n = 0
            while session.get(Product, sku) is not None:
                suffix_n += 1
                sku = f"{sku_base}-{suffix_n}"

            # Compose description
            desc_parts = []
            if bp.get("on_art_text"):
                desc_parts.append(f"On-art: \"{bp.get('on_art_text')}\"")
            if bp.get("visuals"):
                desc_parts.append("Visuals: " + ", ".join([str(v) for v in bp.get("visuals")]))
            if bp.get("style"):
                desc_parts.append("Style: " + str(bp.get("style")))
            if bp.get("target_audience"):
                desc_parts.append("Audience: " + str(bp.get("target_audience")))
            if bp.get("notes"):
                desc_parts.append("Notes: " + str(bp.get("notes")))
            description = "; ".join(desc_parts)[:45000]

            obj = Product(sku=sku, name=name[:255], description=description)
            if price_val is not None:
                obj.price = price_val
            session.add(obj)
            created += 1
        session.commit()

    with get_session() as session:
        session.add(RunLog(job="import_blueprints", status="ok", message=f"{created} created for '{q}'"))
        session.commit()

    return RedirectResponse(url="/products", status_code=303)


@app.get("/api/research/export.json")
def research_export_json(q: str, limit: int = 50):
    return run_research(q, limit=limit)


@app.get("/api/research/export.csv")
def research_export_csv(q: str, limit: int = 50):
    import csv
    from io import StringIO
    data = run_research(q, limit=limit)
    blueprints = (data.get("llm") or {}).get("design_blueprints") or []
    headers = [
        "name","on_art_text","visuals","style","colors","print_area","target_audience","primary_tags","notes"
    ]
    sio = StringIO()
    w = csv.DictWriter(sio, fieldnames=headers)
    w.writeheader()
    for bp in blueprints:
        row = {k: bp.get(k) for k in headers}
        # Flatten lists
        for key in ("visuals","colors","primary_tags"):
            if isinstance(row.get(key), list):
                row[key] = ", ".join([str(x) for x in row[key]])
        w.writerow(row)
    from fastapi.responses import Response
    return Response(content=sio.getvalue(), media_type="text/csv")


@app.post("/api/research/snapshot")
def research_snapshot(q: str = Form(...), limit: int = Form(50)):
    import json
    data = run_research(q, limit=limit)
    with get_session() as s:
        snap = ResearchSnapshot(
            keywords=q,
            limit=limit,
            metrics_json=json.dumps(data.get("metrics") or {}),
            llm_json=json.dumps(data.get("llm") or {}),
        )
        s.add(snap)
        s.add(RunLog(job="research_snapshot", status="ok", message=f"{q} (limit {limit})"))
        s.commit()
    return RedirectResponse(url="/research/snapshots", status_code=303)


@app.get("/research/snapshots")
def research_snapshots_page(request: Request, q: str | None = None):
    with get_session() as s:
        from sqlmodel import desc, select as sql_select
        stmt = sql_select(ResearchSnapshot)
        if q:
            stmt = stmt.where(ResearchSnapshot.keywords.like(f"%{q}%"))
        stmt = stmt.order_by(desc(ResearchSnapshot.created_at)).limit(200)
        rows = s.exec(stmt).all()
    return templates.TemplateResponse(
        "research_snapshots.html",
        {"request": request, "title": "Research Snapshots", "rows": rows, "q": q or ""},
    )


@app.post("/api/products/update")
def update_product(
    sku: str = Form(...),
    name: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    variant_id: Optional[str] = Form(None),
    thumbnail_url: Optional[str] = Form(None),
):
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj is not None:
            if name is not None:
                obj.name = name
            if price is not None and price != "":
                try:
                    obj.price = float(price)
                except ValueError:
                    pass
            if description is not None:
                obj.description = description
            if variant_id is not None and variant_id != "":
                try:
                    obj.variant_id = int(variant_id)
                except ValueError:
                    pass
            if thumbnail_url is not None:
                obj.thumbnail_url = thumbnail_url
            session.add(obj)
            session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/delete")
def delete_product(sku: str = Form(...)):
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj is not None:
            session.delete(obj)
            session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/upload_image")
def upload_product_image(sku: str = Form(...), image: UploadFile = File(...)):
    suffix = Path(image.filename).suffix or ".jpg"
    path = MEDIA_PRODUCTS / f"{sku}{suffix}"
    with open(path, "wb") as f:
        f.write(image.file.read())
    public_url = f"/media/products/{path.name}"
    # If S3 is configured, upload and use S3 URL instead
    try:
        from s3_storage import is_configured as s3_is_configured, upload_file as s3_upload
        if s3_is_configured():
            prefix = os.getenv("S3_PREFIX", "products").strip("/")
            key = f"{prefix}/{path.name}"
            public_url = s3_upload(str(path), key)
    except Exception:
        pass
    with get_session() as session:
        obj = session.get(Product, sku) or Product(sku=sku)
        obj.thumbnail_url = public_url
        session.add(obj)
        session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/etsy")
def product_to_etsy(sku: str = Form(...)):
    from etsy_client import create_listing_draft, publish_listing, upload_listing_image_from_url, upload_listing_image_from_file
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj is None:
            return RedirectResponse(url="/products", status_code=303)
        payload = {
            "sku": obj.sku,
            "title": obj.name or obj.sku,
            "description": (obj.description or "")[:45000],
            "price": obj.price or 19.99,
            "taxonomy_id": 1125,
            "who_made": "i_did",
            "when_made": "made_to_order",
            "is_supply": False,
        }
        status = "ok"; message = None
        try:
            listing_id = create_listing_draft(payload)
            obj.etsy_listing_id = listing_id
            # Try to upload image if present
            if obj.thumbnail_url:
                if obj.thumbnail_url.startswith("http://") or obj.thumbnail_url.startswith("https://"):
                    upload_listing_image_from_url(listing_id, obj.thumbnail_url)
                elif obj.thumbnail_url.startswith("/media/"):
                    local_path = BASE_DIR / obj.thumbnail_url.lstrip("/")
                    if local_path.exists():
                        upload_listing_image_from_file(listing_id, str(local_path))
            session.add(obj)
            session.commit()
        except Exception as e:
            status = "error"; message = str(e)
        finally:
            session.add(RunLog(job="etsy_list", status=status, message=message))
            session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/etsy_publish")
def product_etsy_publish(sku: str = Form(...)):
    from etsy_client import publish_listing
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj and obj.etsy_listing_id:
            try:
                publish_listing(obj.etsy_listing_id)
                session.add(RunLog(job="etsy_publish", status="ok"))
                session.commit()
            except Exception as e:
                session.add(RunLog(job="etsy_publish", status="error", message=str(e)))
                session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/etsy_update")
def product_etsy_update(sku: str = Form(...)):
    from etsy_client import update_listing
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj and obj.etsy_listing_id:
            try:
                update_listing(obj.etsy_listing_id, {
                    "title": obj.name or obj.sku,
                    "description": (obj.description or "")[:45000],
                    "who_made": "i_did",
                    "when_made": "made_to_order",
                    "is_supply": False,
                })
                session.add(RunLog(job="etsy_update", status="ok"))
                session.commit()
            except Exception as e:
                session.add(RunLog(job="etsy_update", status="error", message=str(e)))
                session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/printful")
def product_to_printful(sku: str = Form(...)):
    from printful_client import create_product
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj is None:
            return RedirectResponse(url="/products", status_code=303)
        payload = {
            "sku": obj.sku,
            "name": obj.name or obj.sku,
            "price": obj.price or 19.99,
            "thumbnail": obj.thumbnail_url,
            "variant_id": obj.variant_id or 4011,
        }
        status = "ok"; message = None
        try:
            variant_id, assets = create_product(payload)
            obj.printful_variant_id = variant_id
            session.add(obj)
            session.commit()
        except Exception as e:
            status = "error"; message = str(e)
        finally:
            session.add(RunLog(job="printful_create", status=status, message=message))
            session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.get("/jobs")
def jobs_page(request: Request):
    return templates.TemplateResponse("jobs.html", {"request": request, "title": "Jobs"})


@app.post("/api/run_job")
def run_job(job: str = Form(...)):
    job_map = {
        "list_to_etsy": "jobs.list_to_etsy",
        "pull_metrics": "jobs.pull_metrics",
        "prune_scale": "jobs.prune_scale",
        "weekly_report": "jobs.weekly_report",
        "intake_to_assets": "jobs.intake_to_assets",
    }
    module_name = job_map.get(job)
    status = "ok"
    message = None
    if module_name:
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, "run"):
                mod.run()
            else:
                status = "no_run"
                message = "run() not implemented"
        except Exception as e:
            status = "error"
            message = str(e)
    else:
        status = "unknown"
        message = f"Unknown job: {job}"

    with get_session() as session:
        session.add(RunLog(job=job, status=status, message=message))
        session.commit()

    return RedirectResponse(url="/logs", status_code=303)


@app.get("/logs")
def logs_page(request: Request):
    with get_session() as session:
        logs = session.exec(select(RunLog).order_by(RunLog.created_at.desc())).all()
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs, "title": "Logs"})


@app.get("/schedules")
def schedules_page(request: Request):
    jobs = scheduler.get_jobs()
    return templates.TemplateResponse("schedules.html", {"request": request, "jobs": jobs, "title": "Schedules"})


@app.post("/api/schedules")
def add_schedule(job: str = Form(...), minutes: int = Form(...)):
    from uuid import uuid4
    job_map = {
        "list_to_etsy": "jobs.list_to_etsy",
        "pull_metrics": "jobs.pull_metrics",
        "prune_scale": "jobs.prune_scale",
        "weekly_report": "jobs.weekly_report",
        "intake_to_assets": "jobs.intake_to_assets",
    }
    module_name = job_map.get(job)
    if module_name:
        job_id = f"{job}-" + str(uuid4())[:8]
        def _runner():
            mod = __import__(module_name, fromlist=["run"])
            if hasattr(mod, "run"):
                try:
                    mod.run()
                    with get_session() as s:
                        s.add(RunLog(job=job, status="ok"))
                        s.commit()
                except Exception as e:
                    with get_session() as s:
                        s.add(RunLog(job=job, status="error", message=str(e)))
                        s.commit()
        scheduler.add_job(_runner, 'interval', minutes=minutes, id=job_id, name=job, replace_existing=False)
    return RedirectResponse(url="/schedules", status_code=303)


@app.post("/api/schedules/delete")
def delete_schedule(id: str = Form(...)):
    try:
        scheduler.remove_job(id)
    except Exception:
        pass
    return RedirectResponse(url="/schedules", status_code=303)


@app.get("/integrations")
def integrations_page(request: Request):
    from etsy_auth import get_access_token
    etsy_connected = True if get_access_token() else False
    printful_key_set = True if os.getenv("PRINTFUL_API_KEY") else False
    return templates.TemplateResponse("integrations.html", {"request": request, "etsy_connected": etsy_connected, "printful_key_set": printful_key_set, "title": "Integrations"})


@app.post("/auth/etsy/login")
def etsy_login():
    from uuid import uuid4
    from etsy_auth import etsy_auth_url
    state = str(uuid4())
    url = etsy_auth_url(state)
    return RedirectResponse(url=url, status_code=303)


@app.get("/auth/etsy/callback")
def etsy_callback(code: str = None, state: str = None, error: str = None):
    from etsy_auth import exchange_code
    if error:
        with get_session() as s:
            s.add(RunLog(job="etsy_oauth", status="error", message=error))
            s.commit()
        return RedirectResponse(url="/integrations", status_code=303)
    if code:
        try:
            exchange_code(code)
            with get_session() as s:
                s.add(RunLog(job="etsy_oauth", status="ok", message="connected"))
                s.commit()
        except Exception as e:
            with get_session() as s:
                s.add(RunLog(job="etsy_oauth", status="error", message=str(e)))
                s.commit()
    return RedirectResponse(url="/integrations", status_code=303)


@app.post("/auth/etsy/test")
def test_etsy():
    from etsy_client import create_listing_draft
    try:
        create_listing_draft({"title": "AutoMerch Test", "description": "Test"})
        with get_session() as s:
            s.add(RunLog(job="etsy_test", status="ok"))
            s.commit()
    except Exception as e:
        with get_session() as s:
            s.add(RunLog(job="etsy_test", status="error", message=str(e)))
            s.commit()
    return RedirectResponse(url="/integrations", status_code=303)


@app.post("/auth/printful/test")
def test_printful():
    from printful_client import get_store_metrics
    try:
        get_store_metrics()
        with get_session() as s:
            s.add(RunLog(job="printful_test", status="ok"))
            s.commit()
    except Exception as e:
        with get_session() as s:
            s.add(RunLog(job="printful_test", status="error", message=str(e)))
            s.commit()
    return RedirectResponse(url="/integrations", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

@app.post("/api/products/etsy_add_image_url")
def etsy_add_image_url(sku: str = Form(...), url: str = Form(...)):
    from etsy_client import upload_listing_image_from_url
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj and obj.etsy_listing_id and url:
            try:
                upload_listing_image_from_url(obj.etsy_listing_id, url)
                session.add(RunLog(job="etsy_add_image_url", status="ok"))
                session.commit()
            except Exception as e:
                session.add(RunLog(job="etsy_add_image_url", status="error", message=str(e)))
                session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/etsy_add_image")
def etsy_add_image(sku: str = Form(...), image: UploadFile = File(...)):
    from etsy_client import upload_listing_image_from_file
    local_path = MEDIA_PRODUCTS / f"{sku}-extra-{image.filename}"
    with open(local_path, "wb") as f:
        f.write(image.file.read())
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj and obj.etsy_listing_id:
            try:
                upload_listing_image_from_file(obj.etsy_listing_id, str(local_path))
                session.add(RunLog(job="etsy_add_image_file", status="ok"))
                session.commit()
            except Exception as e:
                session.add(RunLog(job="etsy_add_image_file", status="error", message=str(e)))
                session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/etsy_update_price")
def etsy_update_price(sku: str = Form(...)):
    from etsy_client import update_listing_price
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj and obj.etsy_listing_id and obj.price is not None:
            try:
                update_listing_price(obj.etsy_listing_id, float(obj.price))
                session.add(RunLog(job="etsy_update_price", status="ok"))
                session.commit()
            except Exception as e:
                session.add(RunLog(job="etsy_update_price", status="error", message=str(e)))
                session.commit()
    return RedirectResponse(url="/products", status_code=303)


from fastapi.middleware.cors import CORSMiddleware

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/api/export/products.json")
def export_products_json():
    with get_session() as session:
        rows = session.exec(select(Product)).all()
    return [r.model_dump() for r in rows]


@app.get("/api/export/products.csv")
def export_products_csv():
    import csv
    from io import StringIO
    with get_session() as session:
        rows = session.exec(select(Product)).all()
    headers = ["sku","name","description","price","variant_id","thumbnail_url","etsy_listing_id","printful_variant_id"]
    sio = StringIO()
    w = csv.DictWriter(sio, fieldnames=headers)
    w.writeheader()
    for r in rows:
        d = r.model_dump()
        w.writerow({k: d.get(k) for k in headers})
    from fastapi.responses import Response
    return Response(content=sio.getvalue(), media_type="text/csv")

@app.get("/catalog")
def catalog(request: Request, q: str | None = None, page: int = 1, page_size: int = 20):
    q = q or request.query_params.get("q")
    page = int(request.query_params.get("page", page))
    page_size = max(1, min(100, int(request.query_params.get("page_size", page_size))))
    with get_session() as session:
        from sqlmodel import or_
        stmt = select(Product)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(Product.sku.like(like), Product.name.like(like)))
        total = len(session.exec(stmt).all())
        stmt = stmt.offset((page-1)*page_size).limit(page_size)
        products = session.exec(stmt).all()
    pager = {"page": page, "page_size": page_size, "total": total}
    return templates.TemplateResponse("catalog.html", {"request": request, "products": products, "title": "Catalog", "q": q, "pager": pager})


from fastapi import Request
from fastapi.responses import HTMLResponse

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return HTMLResponse(f"<html><body><h1>404 Not Found</h1><p>{request.url.path}</p></body></html>", status_code=404)




