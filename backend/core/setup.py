from infra.logging import setup_logging
from beanie import init_beanie
from domain.entities.lol.game import Game
from domain.entities.lol.game_series import GameSeries
from domain.entities.lol.tournament import Tournament
from pymongo import AsyncMongoClient
from settings import settings


async def setup():
    setup_logging()
    client = AsyncMongoClient(settings.mongo_url)
    await init_beanie(
        database=client[settings.mongo_db],
        document_models=[Game, GameSeries, Tournament],
    )
