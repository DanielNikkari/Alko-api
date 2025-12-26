import os
import polars
import time
import shutil

from pathlib import Path
from app.schemas.products import Product, Products
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DOWNLOAD_PATH = Path(__file__).parent.parent / "data"

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
    return webdriver.Chrome(options=chrome_options)

def get_newest_sheet(folder: Path) -> Path:
    """Get the most recently modified xlsx file."""
    xlsx_files = list(folder.glob("*.xlsx"))

    if not xlsx_files:
        raise FileNotFoundError(f"No .xlsx files in {str(folder)}")
    
    return max(xlsx_files, key=lambda f: f.stat().st_mtime)
    
def init_product_db() -> polars.DataFrame:
    """
    Initialize the Alko product database into Polars DataFrame.

    Returns:
        polars.DataFrame: Alko product catalog dataframe.
    """
    product_sheet_url = os.getenv('ALKO_PRODUCT_SHEET', "")
    driver: webdriver.Chrome = _init_driver()
    DOWNLOAD_PATH.mkdir(exist_ok=True)
    try:
        driver.get(product_sheet_url)
        time.sleep(5)  # Wait for the download
    except Exception as e:
        raise RuntimeError(f"Unexpected error while getting data sheet from Alko: {e}")
    finally:
        driver.quit()

    try:
        filepath: Path = get_newest_sheet(DOWNLOAD_PATH)
        df = polars.read_excel(source=str(filepath), sheet_name="Alkon Hinnasto Tekstitiedostona", has_header=True, read_options={"skip_rows": 3})
    except Exception as e:
        raise RuntimeError(f"Unexpected error while reading data sheet into DataFrame: {e}")
    finally:
        shutil.rmtree(path=str(DOWNLOAD_PATH))
        DOWNLOAD_PATH.mkdir(exist_ok=True)

    return df