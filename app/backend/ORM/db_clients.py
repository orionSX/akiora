from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
# from aioredis import Redis, from_url


class MongoDB:
    _client: AsyncIOMotorClient | None = None
    _db: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls, uri: str, db_name: str) -> None:
        cls._client = AsyncIOMotorClient(uri)
        cls._db = cls._client[db_name]

    @classmethod
    async def disconnect(cls) -> None:
        if cls._client:
            cls._client.close()

    @classmethod
    async def get_db(cls) -> AsyncIOMotorDatabase:
        if cls._db is None:
            raise RuntimeError("MongoDB not connected!")
        return cls._db


# class RedisClient:
#     _client: Redis | None = None

#     @classmethod
#     async def connect(cls, uri: str) -> None:
#         cls._client = await from_url(
#             uri, encoding="utf-8", decode_responses=True, max_connections=100
#         )

#     @classmethod
#     async def disconnect(cls) -> None:
#         if cls._client:
#             await cls._client.close()
#             cls._client = None

#     @classmethod
#     def get_client(cls) -> Redis:
#         if cls._client is None:
#             raise RuntimeError("Redis not connected!")
#         return cls._client


async def _get_mongo() -> AsyncIOMotorDatabase:
    return MongoDB.get_db()


# async def _get_redis() -> Redis:
#     return RedisClient.get_client()
