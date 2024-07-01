from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.database import collection
from app.models import ProductCreate

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/products/")
async def create_product(product: ProductCreate):
    try:
        product_dict = product.dict()
        result = await collection.insert_one(product_dict)
        created_product = await collection.find_one({"_id": result.inserted_id})
        if created_product:
            created_product["_id"] = str(created_product["_id"])
            return created_product
        else:
            raise HTTPException(status_code=404, detail="Product not found after insertion")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# @app.get("/products/")
# async def get_products():
#     try:
#         products = []
#         async for product in collection.find():
#             product["_id"] = str(product["_id"])
#             products.append(product)
#         return products
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

