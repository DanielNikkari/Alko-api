import os
import logging

from pathlib import Path
from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app.services.products import init_product_db
from app.routers import products

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
API_VERSION = os.getenv("API_VERSION", "v1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server...")
    app.state.products = init_product_db()
    yield
    logger.info("Shutting down...")

app = FastAPI(root_path=f"/api/{API_VERSION}", lifespan=lifespan)

app.include_router(products.router)

@app.get("/")
async def root():
    return "Hello from Alko API!"

@app.get("/health", response_class=HTMLResponse)
async def health():
    html_path = Path(__file__).parent / "templates" / "health.html"
    return html_path.read_text()