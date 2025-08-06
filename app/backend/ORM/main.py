from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db_clients import MongoDB, RedisClient
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDB.connect(os.getenv("MONGO_DB_URI"), "Akiora")
    await RedisClient.connect(os.getenv("REDIS_URI"))

    yield
    await MongoDB.disconnect()
    await RedisClient.disconnect()


origins = ["*"]
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def get():
    return {"Status": "Started"}
