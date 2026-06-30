from contextlib import asynccontextmanager

from beanie import init_beanie
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from granian import Granian
from granian.constants import Interfaces
from pymongo import AsyncMongoClient

from ioc import container
from infra import settings, setup_logging
from modules.auth.routes import router as auth_router
from modules.community.models import Host, User
from modules.community.routes.user import router as user_router
from modules.game.models.game import Game
from modules.game.models.match import Match
from modules.game.models.tournament import Tournament
from modules.game.routes import router as tournament_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    mongo_client = AsyncMongoClient(settings.mongo_url)
    await init_beanie(
        database=mongo_client[settings.mongo_db],
        document_models=[User, Host, Game, Match, Tournament],
    )
    try:
        yield
    finally:
        await mongo_client.close()
        await container.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Akiora Core", lifespan=lifespan)

    @app.get("/health")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(tournament_router)
    setup_dishka(container, app)
    return app


app = create_app()


if __name__ == "__main__":
    server = Granian(
        target="main:create_app",
        address=settings.core_host,
        port=settings.core_port,
        interface=Interfaces.ASGI,
        factory=True,
    )
    server.serve()
