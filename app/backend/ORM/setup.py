from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db_clients import MongoDB, DragonClient
import os


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


origins = ["*"]
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def test_endpoint():
    mongo = MongoDB.get_db()
    collection = mongo["test_collection"]
    await collection.insert_one({"test": "document"})

    redis = DragonClient.get_client()
    await redis.set("test_key", "test_value")
    value = await redis.get("test_key")

    return {"mongo": "ok", "redis": value}
