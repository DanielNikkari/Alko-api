import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.templating import Jinja2Templates

from app.routers import products
from app.services.products import init_product_db

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


app = FastAPI(
    root_path=f"/api/{API_VERSION}",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

app.include_router(products.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    status = "healthy"
    message = None

    try:
        if request.app.state.products is None:
            status = "unhealthy"
            message = "Products data not loaded"
        elif request.app.state.products.height == 0:
            status = "unhealthy"
            message = "Products data is empty"
    except AttributeError:
        status = "unhealthy"
        message = "Application state not initialized"

    product_count = 0
    try:
        if request.app.state.products is not None:
            product_count = len(request.app.state.products)
    except AttributeError:
        pass

    return templates.TemplateResponse(
        request=request,
        name="health.html",
        context={
            "STATUS": status,
            "VERSION": API_VERSION,
            "ENVIRONMENT": ENVIRONMENT,
            "PRODUCT_COUNT": product_count,
            "UPDATE_DATE": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "MESSAGE": message,
        },
        status_code=200 if status == "healthy" else 503,
    )


@app.get("/health", response_class=HTMLResponse)
async def health(request: Request):
    status = "healthy"
    message = None

    try:
        if request.app.state.products is None:
            status = "unhealthy"
            message = "Products data not loaded"
        elif request.app.state.products.height == 0:
            status = "unhealthy"
            message = "Products data is empty"
    except AttributeError:
        status = "unhealthy"
        message = "Application state not initialized"

    product_count = 0
    try:
        if request.app.state.products is not None:
            product_count = len(request.app.state.products)
    except AttributeError:
        pass

    return templates.TemplateResponse(
        request=request,
        name="health.html",
        context={
            "STATUS": status,
            "VERSION": API_VERSION,
            "ENVIRONMENT": ENVIRONMENT,
            "PRODUCT_COUNT": product_count,
            "UPDATE_DATE": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "MESSAGE": message,
        },
        status_code=200 if status == "healthy" else 503,
    )


@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    """Get product statistics page."""
    df = request.app.state.products

    # Get top types
    top_types = (
        df.group_by("Tyyppi").len().sort("len", descending=True).head(5).to_dicts()
    )
    top_types = [{"type": item["Tyyppi"], "count": item["len"]} for item in top_types]

    # Get top countries
    top_countries = (
        df.group_by("Valmistusmaa")
        .len()
        .sort("len", descending=True)
        .head(5)
        .to_dicts()
    )
    top_countries = [
        {"country": item["Valmistusmaa"], "count": item["len"]}
        for item in top_countries
    ]

    return templates.TemplateResponse(
        request=request,
        name="stats.html",
        context={
            "TOTAL_PRODUCTS": f"{df.height:,}",
            "PRICE_MIN": df["Hinta"].min(),
            "PRICE_MAX": df["Hinta"].max(),
            "PRICE_AVG": round(df["Hinta"].mean(), 2),
            "ALCOHOL_MIN": df["Alkoholi-%"].min(),
            "ALCOHOL_MAX": df["Alkoholi-%"].max(),
            "ALCOHOL_AVG": round(df["Alkoholi-%"].mean(), 1),
            "TOP_TYPES": top_types,
            "TOP_COUNTRIES": top_countries,
        },
    )
