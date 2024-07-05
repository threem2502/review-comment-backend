from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.database import collection
from app.models import ProductCreate
from app.models import Review
from app.models import ListReview
import pickle
import asyncio
from pyvi import ViTokenizer
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd

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
        # Create a DataFrame with the product data
        df = pd.DataFrame([product_dict])
        data = pd.read_csv('products.csv')
        if (product_dict['brand'] in list(data['brand']) and product_dict['product_name'] in list(data['product_name'])):
            return "Đã có trong products"

        with open('products.csv', mode='a+', newline='', encoding='utf-8') as file:
            # Check if the file is empty
            file.seek(0, 2)  # Move to the end of the file
            if file.tell() == 0:
                df.to_csv(file, header=True, index=False, encoding='utf-8')
            else:
                df.to_csv(file, header=False, index=False, encoding='utf-8')

        return product_dict
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
@app.get("/products/")
async def get_products():
    try:
        products = []

        # Load data from CSV into a DataFrame
        df = pd.read_csv('products.csv', encoding='utf-8')

        # Convert DataFrame rows to dictionaries
        products = df.to_dict('records')

        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# Load model and tokenizer
model = load_model('tiki-model.keras')
with open("tokenizer_data.pkl", "rb") as input_file:
    my_tokenizer = pickle.load(input_file)

def preprocessing_input(text, tokenizer, max_length=128):
    text = text.lower()
    tokenized_text = ViTokenizer.tokenize(text)
    sequences = tokenizer.texts_to_sequences([tokenized_text])
    padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post')
    return padded_sequences

@app.post("/detect/")
async def get_detect(review: Review):
    inp_text = preprocessing_input(review.text, my_tokenizer)
    result = model.predict(inp_text)[0]
    percentages = (result / np.sum(result)) * 100  # Calculate percentages
    response = {
        "Tốt": f"{percentages[2]:.2f}%",
        "Bình thường": f"{percentages[1]:.2f}%",
        "Tệ": f"{percentages[0]:.2f}%"
    }
    return response


@app.post("/detect_product/", response_model=dict)
async def get_detect_product(reviews: ListReview ):
    try:
        async def process_review(review):
            inp_text = preprocessing_input(review, my_tokenizer)
            result = model.predict(inp_text)[0]
            percentages = {
                "Tốt": result[2],
                "Bình thường": result[1],
                "Tệ": result[0]
            }
            return percentages
        
        tasks = [process_review(review) for review in reviews.list_text]
        results = await asyncio.gather(*tasks)

        # Initialize counters
        good_count = 0
        normal_count = 0
        bad_count = 0

        # Count reviews based on highest percentage category
        for result in results:
            max_percentage = max(result.values())
            if result["Tốt"] == max_percentage:
                good_count += 1
            elif result["Tệ"] == max_percentage:
                bad_count += 1
            else:
                normal_count += 1
        
        response = {
            "Tốt": good_count,
            "Bình thường": normal_count,
            "Tệ": bad_count
        }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")