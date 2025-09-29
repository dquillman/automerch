import importlib
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from db import init_db, get_session
from models import Product, RunLog

app = FastAPI(title="AutoMerch")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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
