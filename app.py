import importlib
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import select

from db import init_db, get_session
from models import Product, RunLog

app = FastAPI(title="AutoMerch")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
scheduler = BackgroundScheduler()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Home"})


@app.get("/products")
def products_page(request: Request):
    with get_session() as session:
        products = session.exec(select(Product)).all()
    return templates.TemplateResponse("products.html", {"request": request, "products": products, "title": "Products"})


@app.post("/api/products")
def add_product(sku: str = Form(...)):
    with get_session() as session:
        if session.get(Product, sku) is None:
            session.add(Product(sku=sku))
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

@app.post("/api/products/delete")
def delete_product(sku: str = Form(...)):
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj is not None:
            session.delete(obj)
            session.commit()
    return RedirectResponse(url="/products", status_code=303)

@app.on_event("startup")
def start_scheduler():
    scheduler.start()


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
        # Import lazily to avoid keeping modules pinned
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

@app.post("/api/products")
def add_product(sku: str = Form(...), name: str = Form(None), price: str = Form(None), description: str = Form(None)):
    with get_session() as session:
        obj = session.get(Product, sku)
        if obj is None:
            obj = Product(sku=sku)
        if name:
            obj.name = name
        if price:
            try:
                obj.price = float(price)
            except ValueError:
                pass
        if description:
            obj.description = description
        session.add(obj)
        session.commit()
    return RedirectResponse(url="/products", status_code=303)


@app.post("/api/products/update")
def update_product(sku: str = Form(...), name: str = Form(None), price: str = Form(None), description: str = Form(None)):
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
            session.add(obj)
            session.commit()
    return RedirectResponse(url="/products", status_code=303)
