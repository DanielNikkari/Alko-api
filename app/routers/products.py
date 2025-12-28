import logging

import polars
from fastapi import APIRouter, Query, Request
from pydantic import TypeAdapter

import app.services.products as product_service
from app.schemas.products import Product

logger = logging.getLogger(__file__)

router = APIRouter(
    prefix="/products", tags=["products"], responses={404: {"descirption": "Not found"}}
)


@router.get("/", response_model=list[Product])
async def get_all_products(request: Request):
    """Get all products."""
    logger.info("Getting all products...")
    df = request.app.state.products.df
    adapter = TypeAdapter(list[Product])
    products = adapter.validate_python(df.to_dicts())
    return products


@router.get("/queryProducts")
async def query_products(
    request: Request,
    name: str = None,
    producer: str = None,
    product_type: str = None,
    subtype: str = None,
    country: str = None,
    area: str = None,
    vintage: str = None,
    grapes: str = None,
    special_group: str = None,
    beer_type: str = None,
    package_type: str = None,
    closure_type: str = None,
    assortment: str = None,
    min_price: float = None,
    max_price: float = None,
    min_alcohol: float = None,
    max_alcohol: float = None,
    min_sugar: float = None,
    max_sugar: float = None,
    limit: int = Query(100, ge=1, description="Max results"),
):
    """Query products with extended filtering options."""
    logger.info("Querying products...")
    df = request.app.state.products.df
    adapter = TypeAdapter(list[Product])
    results = product_service.search_products(
        df,
        name=name,
        producer=producer,
        product_type=product_type,
        subtype=subtype,
        country=country,
        area=area,
        vintage=vintage,
        grapes=grapes,
        special_group=special_group,
        beer_type=beer_type,
        package_type=package_type,
        closure_type=closure_type,
        assortment=assortment,
        min_price=min_price,
        max_price=max_price,
        min_alcohol=min_alcohol,
        max_alcohol=max_alcohol,
        min_sugar=min_sugar,
        max_sugar=max_sugar,
    )
    results = results.head(limit).to_dicts()
    products = adapter.validate_python(results)
    return products


@router.get("/productTypes")
async def get_product_types(request: Request):
    """Get unique product types."""
    logger.info("Getting unique product types.")
    df = request.app.state.products.df
    return product_service.get_product_types(df)


@router.get("/producers")
async def get_producers(request: Request):
    """Get unique producers, such as vineyards."""
    logger.info("Getting unique producers.")
    df = request.app.state.products.df
    return product_service.get_producers(df)


@router.get("/countries")
async def get_countries(request: Request):
    """Get unique countries of origin."""
    logger.info("Getting unique countries.")
    df = request.app.state.products.df
    return product_service.get_countries(df)


@router.get("/areas")
async def get_areas(request: Request):
    """Get unique areas of origin."""
    logger.info("Getting unique areas.")
    df = request.app.state.products.df
    return product_service.get_areas(df)


@router.get("/{product_id}")
async def get_product_by_id(request: Request, product_id: str):
    """Get product by ID."""
    logger.info(f"Getting product by ID {product_id}")
    df = request.app.state.products.df
    adapter = TypeAdapter(list[Product])
    results = df.filter(polars.col("Numero").cast(polars.Utf8) == product_id).to_dicts()
    products = adapter.validate_python(results)
    return products
