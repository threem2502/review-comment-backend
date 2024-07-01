from pydantic import BaseModel

class ProductCreate(BaseModel):
    image: str
    rating_average: float
    reviews_count: int
    brand: str
    product_name: str
