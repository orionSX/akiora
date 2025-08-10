from fastapi import Depends
from db_clients import _get_redis, Redis
from datetime import timedelta
from typing import Dict, Any, List, TypeVar, Generic, Type
import pickle
import zlib
from models.Document import Document
from bson import ObjectId
from pydantic import validate_call, ConfigDict

# orjson could be used maybe idk yet
validate_call = validate_call(config=ConfigDict(arbitrary_types_allowed=True))
T = TypeVar("T", bound=Document)


class DragonManager(Generic[T]):
    _model_class: Type[T]

    @classmethod
    def _get_data_storage(cls) -> str:
        return f"Dragon : = {(cls._model_class.__name__.lower() + 's',)}"

    @classmethod
    async def get_data(cls, key: str, cache: Redis = Depends(_get_redis)) -> T | None:
        raw_data = await cache.get(key)
        if raw_data:
            return pickle.load(zlib.decompress(raw_data))
        return None

    @classmethod
    async def set_data(
        cls,
        key: str,
        data: T,
        ex: int | timedelta | None,
        cache: Redis = Depends(_get_redis),
    ) -> bool:
        match ex:
            case None:
                await cache.set(key, zlib.compress(pickle.dumps(data), level=6))
                return True
            case _:
                await cache.set(key, zlib.compress(pickle.dumps(data), level=6), ex=ex)
                return True

    @classmethod
    async def _get_valid_key(
        cls, key: Dict[str, Any] | str | ObjectId | List[str | ObjectId]
    ) -> str:
        base_str = cls._model_class.__name__.lower() + "s:"
        if isinstance(key, ObjectId):
            base_str += str(key)
        elif isinstance(key, str):
            base_str += key
        elif isinstance(key, Dict[str, Any]):
            base_str += await cls._serialize_key(key)
        elif isinstance(key, List[str | ObjectId]):
            base_str += ":".join(str(x) for x in key)
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
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId],
        many: bool = False,
        by_id: bool = False,
    ) -> List[T] | T | None:
        valid_key = await cls._get_valid_key(query)
        data = await cls.get_data(key=valid_key)
        if data:
            match many:
                case True:
                    if not isinstance(data, List):
                        raise
                    return data

                case False:
                    return data
                case _:
                    raise
        return data

    @classmethod
    async def delete(
        cls,
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId],
        cache: Redis = Depends(_get_redis),
        many: bool = False,
        by_id: bool = False,
    ) -> bool:
        valid_key = await cls._get_valid_key(query)
        await cache.unlink(valid_key)
        return True

    @classmethod
    async def create(
        cls,
        update_data: T | Dict[str, Any],
        many: bool = False,
    ) -> T | Dict[str, Any] | List[T] | Dict[str, Any]:
        valid_key = await cls._get_valid_key("last_created")
        await cls.set_data(key=valid_key, data=update_data, ex=timedelta(hours=1))

        return await cls.get(
            query="last_created",
            many=many,
        )

    @classmethod
    async def update(
        cls,
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId],
        update_data: T,
        many: bool = False,
        by_id: bool = False,
    ) -> bool:
        valid_key = await cls._get_valid_key(query)
        await cls.set_data(key=valid_key, data=update_data, ex=timedelta(hours=1))

        return True
