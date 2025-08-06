from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoDB:
    _client: AsyncIOMotorClient = None
    _db: AsyncIOMotorDatabase = None

    @classmethod
    def connect(cls, uri: str, db_name: str)->None:
        cls._client = AsyncIOMotorClient(uri)
        cls._db = cls._client[db_name]
        

    @classmethod
    def disconnect(cls)->None:
        if cls._client:
            cls._client.close()

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        if cls._db is None:
            raise RuntimeError("MongoDB not connected!")
        return cls._db

async def _get_db()->AsyncIOMotorDatabase:
    return MongoDB.get_db()

