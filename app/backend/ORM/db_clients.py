from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from redis.asyncio.connection import ConnectionPool
from redis.asyncio import Redis

# TODO : create indexes on startup for mongo


class MongoDB:
    _client: AsyncIOMotorClient | None = None
    _db: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls, uri: str, db_name: str) -> None:
        cls._client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )
        cls._db = cls._client[db_name]

    @classmethod
    async def disconnect(cls) -> None:
        if cls._client:
            cls._client.close()

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        if cls._db is None:
            raise RuntimeError("MongoDB not connected!")
        return cls._db


class DragonClient:
    _pool: ConnectionPool | None = None
    _client: Redis | None = None

    @classmethod
    async def connect(cls, uri: str) -> None:
        cls._pool = ConnectionPool.from_url(uri)
        cls._client = Redis.from_pool(cls._pool)

    @classmethod
    async def disconnect(cls) -> None:
        if cls._client:
            await cls._client.aclose()
            cls._client = None

    @classmethod
    def get_client(cls) -> Redis:
        if cls._client is None:
            raise RuntimeError("Redis not connected!")
        return cls._client


def _get_mongo(key: str | None = None) -> AsyncIOMotorCollection | AsyncIOMotorDatabase:
    db = MongoDB.get_db()
    if key:
        return db[key]
    return db


def _get_dragon():
    return DragonClient.get_client()
