import pytest

import app.services.products as ps
from app.schemas.products import Products, Product

def test_init_product_db(request):
    """
    >>> uv run pytest tests/test_products_service.py::test_init_product_db
    """
    products = ps.init_product_db()