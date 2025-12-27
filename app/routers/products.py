from fastapi import APIRouter, HTTPException, Request, Response
from app.schemas.products import Product
from pydantic import TypeAdapter

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"descirption": "Not found"}}
)

@router.get("/", response_model=list[Product])
async def get_all_products(request: Request):
    """Get all products."""
    df = request.app.state.products
    adapter = TypeAdapter(list[Product])
    products = adapter.validate_python(df.to_dicts())
    return products