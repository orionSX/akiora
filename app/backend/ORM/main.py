from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import MongoDB
import os


@asynccontextmanager
async def lifespan(app: FastAPI):   
    MongoDB.connect(os.getenv('MONDODB_URI',"mongodb://localhost:27011"), "Akiora")
    yield
    MongoDB.disconnect()


origins = ["*"]
app=FastAPI(lifespan=lifespan)
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
