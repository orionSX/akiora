from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db_clients import MongoDB
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDB.connect(
        os.getenv("MONGO_DB_URI", "mongodb://localhost:27011"), "Akiora"
    )

    yield
    await MongoDB.disconnect()


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
