from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db_clients import MongoDB, DragonClient
from settings import lifespan, ORIGINS


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
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
