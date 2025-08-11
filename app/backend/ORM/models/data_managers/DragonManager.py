from fastapi import Depends
from db_clients import _get_redis, Redis
from datetime import timedelta
from typing import Dict, Any, List, TypeVar, Generic, Type
import pickle
import zlib
from models.Document import Document
from pydantic import validate_call, ConfigDict

# orjson could be used maybe idk yet
validate_call = validate_call(config=ConfigDict(arbitrary_types_allowed=True))
T = TypeVar("T", bound=Document)

_CACHE_EXPIRE_TIME = timedelta(hours=3)


class DragonManager(Generic[T]):
    _model_class: Type[T]

    @classmethod
    def _get_data_storage(cls) -> str:
        return f"Dragon : = {(cls._model_class.__name__.lower() + 's',)}"

    @classmethod
    async def get_data(
        cls, key: str, cache: Redis = Depends(_get_redis)
    ) -> List[Dict[str, Any]]:
        raw_data = await cache.get(key)
        if raw_data:
            return pickle.load(zlib.decompress(raw_data))
        return []

    @classmethod
    async def set_data(
        cls,
        key: str,
        data: List[Dict[str, Any]] | Dict[str, Any],
        cache: Redis = Depends(_get_redis),
    ) -> bool:
        await cache.set(
            key, zlib.compress(pickle.dumps(data), level=6), ex=_CACHE_EXPIRE_TIME
        )
        return True

    @classmethod
    async def _get_valid_key(cls, key: Dict[str, Any]) -> str:
        base_str = cls._model_class.__name__.lower() + "s:"
        base_str += await cls._serialize_key(key)
        return base_str

    @classmethod
    async def _serialize_key(cls, key_dict: Dict[str, Any]) -> str:
        escaped_items = []
        for key, value in sorted(key_dict.items()):
            esc_key = (
                str(key).replace("\\", "\\\\").replace("|", "\\|").replace("=", "\\=")
            )
            esc_value = (
                str(value).replace("\\", "\\\\").replace("|", "\\|").replace("=", "\\=")
            )
            escaped_items.append(f"{esc_key}={esc_value}")

        return "|".join(escaped_items)

    @classmethod
    async def get(
        cls,
        query: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        valid_key = await cls._get_valid_key(query)
        return await cls.get_data(key=valid_key)

    @classmethod
    async def delete(
        cls,
        query: Dict[str, Any],
        cache: Redis = Depends(_get_redis),
    ) -> bool:
        valid_key = await cls._get_valid_key(query)
        await cache.unlink(valid_key)
        return True

    @classmethod
    async def create(
        cls,
        create_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        valid_key = await cls._get_valid_key({"last_created": True})
        await cls.set_data(key=valid_key, data=create_data)

        return await cls.get(
            query={"last_created": True},
        )

    @classmethod
    async def update(
        cls,
        query: Dict[str, Any],
        update_data: Dict[str, Any],
    ) -> bool:
        valid_key = await cls._get_valid_key(query)
        await cls.set_data(key=valid_key, data=update_data)

        return True
