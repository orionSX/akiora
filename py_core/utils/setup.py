from utils.logging import setup_logging
from beanie import init_beanie
from models import db_models
from pymongo import AsyncMongoClient
from utils.settings import settings


async def setup():
    setup_logging()
    client = AsyncMongoClient(settings.mongo_url)
    await init_beanie(
        database=client[settings.mongo_db],
        document_models=db_models,
    )
