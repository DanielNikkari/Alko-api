import os
import logging

from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.services.products import init_product_db
from app.routers import products

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
API_VERSION = os.getenv("API_VERSION", "v1")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server...")
    app.state.products = init_product_db()
    yield
    logger.info("Shutting down...")

app = FastAPI(root_path=f"/api/{API_VERSION}", lifespan=lifespan, default_response_class=ORJSONResponse)

app.include_router(products.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="health.html",
        context={
            "STATUS": "healthy",
            "VERSION": API_VERSION,
            "ENVIRONMENT": ENVIRONMENT,
            "PRODUCT_COUNT": len(request.app.state.products),
            "UPDATE_DATE": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )

@app.get("/health", response_class=HTMLResponse)
async def health(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="health.html",
        context={
            "STATUS": "healthy",
            "VERSION": API_VERSION,
            "ENVIRONMENT": ENVIRONMENT,
            "PRODUCT_COUNT": len(request.app.state.products),
            "UPDATE_DATE": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )