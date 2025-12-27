import sys

try:
    import logging
    import os

    import requests
    from dotenv import load_dotenv
    from fastmcp import FastMCP
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

logger.info("Starting MCP server...")

load_dotenv()

MCP_PORT = os.getenv("MCP_PORT")
MCP_HOST = os.getenv("HOST")
TRANSPORT = os.getenv("TRANSPORT", "stdio")
ALKO_API_BASE_URL = os.getenv("BASE_URL")
ALKO_API_API_VERSION = os.getenv("API_VERSION")

mcp = FastMCP("Alko Product MCP Server")


@mcp.tool(
    name="find_alko_products",
    description="Search the product database with search terms.",
)
def search_products(
    limit: int,
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
):
    params = {k: v for k, v in locals().items() if v is not None}

    response = requests.get(
        f"{ALKO_API_BASE_URL}/api/{ALKO_API_API_VERSION}/products/queryProducts",
        params=params,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    try:
        logger.info(f"BASE_URL: {ALKO_API_BASE_URL}")
        logger.info(f"TRANSPORT: {TRANSPORT}")
        logger.info(f"MCP HOST: {MCP_HOST} and PORT: {MCP_PORT}")
        if TRANSPORT == "stdio":
            mcp.run()
        else:
            mcp.run(transport=TRANSPORT, host=MCP_HOST, port=int(MCP_PORT))
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
