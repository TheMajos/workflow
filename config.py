import os
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "TDA")
MONGO_DB_COLLECTION = os.getenv("MONGODB_COLLECTION", "UserStore")
MONGO_DB_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_DB_PORT = int(os.getenv("MONGO_DB_PORT", "27017"))
MONGO_DB_CONNECTION = AsyncIOMotorClient(host=MONGO_DB_HOST, port=MONGO_DB_PORT)

JWT_ALGORITHM = "HS256"

SECRET_KEY = os.getenv("SECRET_KEY")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB_ZERO = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
)
REDIS_DB_ONE = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True
)
