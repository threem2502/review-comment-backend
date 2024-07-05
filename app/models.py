from pydantic import BaseModel
from typing import List
class ProductCreate(BaseModel):
    image: str
    rating_average: float
    reviews_count: int
    brand: str
    product_name: str

class Review(BaseModel):
    text: str

class ListReview(BaseModel):
    list_text: List[str]