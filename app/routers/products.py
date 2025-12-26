from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"descirption": "Not found"}}
)

@router.get("/")
async def get_all_products():
    pass