import json
import logging
from datetime import datetime
from functools import reduce
from pathlib import Path

import polars

from app.schemas.products import ProductDatabase

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent.parent.parent / "data"


def init_product_db() -> ProductDatabase:
    """Load the pre-fetched product database with metadata."""
    logger.info("Loading product database...")

    parquet_path = DATA_PATH / "products.parquet"
    metadata_path = DATA_PATH / "metadata.json"

    if not parquet_path.exists():
        raise FileNotFoundError(
            f"Product data not found at {parquet_path}. "
            "Run 'uv run python -m scraper.fetch_products' first."
        )

    df = polars.read_parquet(parquet_path)

    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text())
        updated_at = datetime.fromisoformat(metadata["updated_at"])
    else:
        updated_at = datetime.fromtimestamp(parquet_path.stat().st_mtime)

    logger.info(f"Loaded {len(df)} products (updated: {updated_at}).")

    return ProductDatabase(
        df=df,
        updated_at=updated_at,
        product_count=len(df),
    )


def search_products(
    df: polars.DataFrame,
    name: str | None = None,
    producer: str | None = None,
    product_type: str | None = None,
    subtype: str | None = None,
    country: str | None = None,
    area: str | None = None,
    vintage: str | None = None,
    grapes: str | None = None,
    special_group: str | None = None,
    beer_type: str | None = None,
    package_type: str | None = None,
    closure_type: str | None = None,
    assortment: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_alcohol: float | None = None,
    max_alcohol: float | None = None,
    min_sugar: float | None = None,
    max_sugar: float | None = None,
) -> polars.DataFrame:
    """Find products with extended filtering options."""
    string_column_mapping = {
        "Nimi": name,
        "Valmistaja": producer,
        "Tyyppi": product_type,
        "Alatyyppi": subtype,
        "Valmistusmaa": country,
        "Alue": area,
        "Vuosikerta": vintage,
        "Rypäleet": grapes,
        "Erityisryhmä": special_group,
        "Oluttyyppi": beer_type,
        "Pakkaustyyppi": package_type,
        "Suljentatyyppi": closure_type,
        "Valikoima": assortment,
    }

    filters = [
        polars.col(col).fill_null("").str.to_lowercase().str.contains(val.lower())
        for col, val in string_column_mapping.items()
        if val and val != "*"
    ]

    if min_price is not None:
        filters.append(polars.col("Hinta") >= min_price)
    if max_price is not None:
        filters.append(polars.col("Hinta") <= max_price)
    if min_alcohol is not None:
        filters.append(polars.col("Alkoholi-%") >= min_alcohol)
    if max_alcohol is not None:
        filters.append(polars.col("Alkoholi-%") <= max_alcohol)
    if min_sugar is not None:
        filters.append(polars.col("Sokeri g/l") >= min_sugar)
    if max_sugar is not None:
        filters.append(polars.col("Sokeri g/l") <= max_sugar)

    if filters:
        df = df.filter(reduce(lambda a, b: a & b, filters))

    logger.info(f"Found {len(df)} results after filtering.")

    return df
