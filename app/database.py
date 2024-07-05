from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb+srv://threem2502:manh2502@tiki-product.zqddyvz.mongodb.net/?retryWrites=true&w=majority&appName=tiki-product"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.mydatabase  
collection = database.products
