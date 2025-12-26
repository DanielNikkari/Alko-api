import pydantic

class Product(pydantic.BaseModel):
    name: str
    taste_type: str
    country: str
    description: str
    price: float
    link: str
    image_link: str|None=None
    volume:str|None=None

class Products(pydantic.BaseModel):
    products: list[Product]
    product_count: int
    query_parameter: str