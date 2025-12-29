#!/usr/bin/env python3
"""Standalone script to fetch Alko product data."""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

import polars
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DOWNLOAD_PATH = Path(__file__).parent / "temp_downloads"
OUTPUT_PATH = Path(__file__).parent.parent / "data"


def _init_driver() -> webdriver.Chrome:
    """Initialize a Selenium webdriver instance."""
    chrome_options = Options()
    prefs = {
        "download.default_directory": str(DOWNLOAD_PATH),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)


def get_newest_sheet(folder: Path) -> Path:
    """Get the most recently modified xlsx file."""
    xlsx_files = list(folder.glob("*.xlsx"))
    if not xlsx_files:
        raise FileNotFoundError(f"No .xlsx files in {folder}")
    return max(xlsx_files, key=lambda f: f.stat().st_mtime)


def wait_for_download_to_finish(
    driver: webdriver.Chrome, directory: Path, timeout: int = 30
) -> Path:
    """Wait for the file to finish downloading."""

    def download_complete(driver):
        xlsx_files = list(directory.glob("*.xlsx"))
        crdownload_files = list(directory.glob("*.crdownload"))
        if xlsx_files and not crdownload_files:
            return xlsx_files[0]
        return False

    return WebDriverWait(driver=driver, timeout=timeout).until(download_complete)


def fetch_and_process() -> polars.DataFrame:
    """Download and process the Alko product sheet."""
    logger.info("Fetching product data from Alko...")

    product_sheet_url = os.getenv("ALKO_PRODUCT_SHEET", "")
    if not product_sheet_url:
        raise ValueError("ALKO_PRODUCT_SHEET environment variable not set")

    DOWNLOAD_PATH.mkdir(exist_ok=True)
    driver = _init_driver()

    try:
        driver.get(product_sheet_url)
        filepath = wait_for_download_to_finish(driver, DOWNLOAD_PATH, timeout=30)
    finally:
        driver.quit()

    logger.info(f"Processing {filepath}...")

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

    # Cleanup temp downloads
    shutil.rmtree(DOWNLOAD_PATH)

    return df


def main():
    """Main entry point."""
    OUTPUT_PATH.mkdir(exist_ok=True)

    df = fetch_and_process()

    output_file = OUTPUT_PATH / "products.parquet"
    metadata_file = OUTPUT_PATH / "metadata.json"

    df.write_parquet(output_file)

    metadata = {
        "updated_at": datetime.now().isoformat(),
        "product_count": len(df),
    }
    metadata_file.write_text(json.dumps(metadata))

    logger.info(f"Saved {len(df)} products to {output_file}")


if __name__ == "__main__":
    main()
