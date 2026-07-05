from contextlib import asynccontextmanager
import time

from beanie import init_beanie
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request

from pymongo import AsyncMongoClient
from loguru import logger

from utils.ioc import container
from utils.logging import setup_logging
from utils.settings import settings
from models import db_models
from gateways.api.auth import auth_router
from gateways.api.community import user_router, host_router
from gateways.api.admin import admin_router
from gateways.api.game import tournament_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    mongo_client = AsyncMongoClient(settings.mongo_url)
    logger.info("Pinging MongoDB...")
    p = await mongo_client[settings.mongo_db].command("ping")
    logger.info(f"MongoDB is reachable: {p}")
    await init_beanie(
        database=mongo_client[settings.mongo_db],
        document_models=db_models,
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

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "{method} {path} → {status} ({duration:.1f}ms)",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration_ms,
        )
        return response

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(tournament_router)
    app.include_router(host_router)
    app.include_router(admin_router)
    setup_dishka(container, app)
    return app
