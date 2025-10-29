from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "selenium_mcp")

_client = None
db = None

def init_db():
    global _client, db
    _client = AsyncIOMotorClient(MONGO_URI)
    db = _client[DB_NAME]
    return db
