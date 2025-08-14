from contextlib import asynccontextmanager
from fastapi import FastAPI
from db_clients import MongoDB, DragonClient
import os
from datetime import timedelta


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_uri = os.getenv("MONGO_DB_URI", "")
    redis_uri = os.getenv("REDIS_URI", "")

    try:
        await MongoDB.connect(mongo_uri, "Akiora")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        raise

    try:
        await DragonClient.connect(redis_uri)
    except Exception as e:
        print(f"Redis connection failed: {e}")
        raise

    yield
    await MongoDB.disconnect()
    await DragonClient.disconnect()


ORIGINS = ["*"]
CACHE_EXPIRE_TIME = timedelta(hours=3)
