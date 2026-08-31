import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "test_db")

client = AsyncIOMotorClient(MONGO_URI)

database = client[DATABASE_NAME]

users_collection = database["users"]