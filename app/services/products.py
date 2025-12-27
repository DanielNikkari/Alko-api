import logging
import os
import shutil
import time
from functools import reduce
from pathlib import Path

import polars
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

DOWNLOAD_PATH = Path(__file__).parent.parent / "data"


def _init_driver() -> webdriver.Chrome:
    """Initialize a Selenium webdriver instance."""
    logger.info("Initializing webdriver")
    chrome_options = Options()
    prefs = {
        "download.default_directory": str(DOWNLOAD_PATH),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")
    return webdriver.Chrome(options=chrome_options)


def get_newest_sheet(folder: Path) -> Path:
    """Get the most recently modified xlsx file."""
    xlsx_files = list(folder.glob("*.xlsx"))

    if not xlsx_files:
        logger.warning(f"No .xlsx files in {str(folder)}")
        raise FileNotFoundError(f"No .xlsx files in {str(folder)}")

    return max(xlsx_files, key=lambda f: f.stat().st_mtime)


def init_product_db() -> polars.DataFrame:
    """
    Initialize the Alko product database into Polars DataFrame.

    Returns:
        polars.DataFrame: Alko product catalog dataframe.
    """
    product_sheet_url = os.getenv("ALKO_PRODUCT_SHEET", "")
    driver: webdriver.Chrome = _init_driver()
    DOWNLOAD_PATH.mkdir(exist_ok=True)
    try:
        driver.get(product_sheet_url)
        time.sleep(5)  # Wait for the download
    except Exception as e:
        logger.error(f"Unexpected error while getting data sheet from Alko: {e}")
        raise RuntimeError(
            f"Unexpected error while getting data sheet from Alko: {e}"
        ) from e
    finally:
        driver.quit()

    try:
        filepath: Path = get_newest_sheet(DOWNLOAD_PATH)
        df = polars.read_excel(
            source=str(filepath),
            sheet_name="Alkon Hinnasto Tekstitiedostona",
            engine="xlsx2csv",
            read_options={
                "skip_rows": 3,
                "schema_overrides": {
                    "Nimi": polars.Utf8,
                    "Valmistaja": polars.Utf8,
                    "Hinnastojärjestyskoodi": polars.Utf8,
                    "Numero": polars.Utf8,
                    "EAN": polars.Utf8,
                    "Luonnehdinta": polars.Utf8,
                    "Rypäleet": polars.Utf8,
                },
            },
        )
        df = df.with_columns(polars.col("Uutuus").is_not_null())
        df = df.with_columns(
            polars.col(polars.Utf8).str.replace_all("\xa0", " ").str.strip_chars()
        )
    except Exception as e:
        logger.error(f"Unexpected error while reading data sheet into DataFrame: {e}")
        raise RuntimeError(
            f"Unexpected error while reading data sheet into DataFrame: {e}"
        ) from e
    finally:
        shutil.rmtree(path=str(DOWNLOAD_PATH))
        DOWNLOAD_PATH.mkdir(exist_ok=True)

    return df


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
    """
    Find products with extended filtering options.

    Args:
        df: DataFrame of the products.
        name: Name of the product (Nimi).
        producer: Producer of the product (Valmistaja).
        product_type: Type, e.g., punaviinit (Tyyppi).
        subtype: Subtype of the product (Alatyyppi).
        country: Origin country of the product (Valmistusmaa).
        area: Area from which the product is from (Alue).
        vintage: Vintage year (Vuosikerta).
        grapes: Grape varieties (Rypäleet).
        special_group: Special group, e.g., vegan (Erityisryhmä).
        beer_type: Beer type (Oluttyyppi).
        package_type: Package type (Pakkaustyyppi).
        closure_type: Closure type (Suljentatyyppi).
        assortment: Assortment type (Valikoima).
        min_price: Minimum price (Hinta).
        max_price: Maximum price (Hinta).
        min_alcohol: Minimum alcohol percentage (Alkoholi-%).
        max_alcohol: Maximum alcohol percentage (Alkoholi-%).
        min_sugar: Minimum sugar content g/l (Sokeri g/l).
        max_sugar: Maximum sugar content g/l (Sokeri g/l).

    Returns:
        Products (polars.DataFrame): DataFrame of the filtered products.
    """
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
