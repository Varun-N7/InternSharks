import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_USERNAME=os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD=os.getenv("MONGODB_PASSWORD")
MONGODB_URI=os.getenv("MONGODB_URI")

client=AsyncIOMotorClient(MONGODB_URI)

database=client["student_management"]

student_collection=database["students"]