from fastapi import Depends
from db_clients import _get_redis, Redis
from datetime import timedelta
from typing import Dict, Any, List, TypeVar
import pickle
import zlib
# orjson could be used maybe idk yet

T = TypeVar("T")


class DragonManager:
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
        if ex is not None and not isinstance(ex, (int, timedelta)):
            raise
        match ex:
            case None:
                await cache.set(key, zlib.compress(pickle.dumps(data), level=6))
                return True
            case _:
                await cache.set(key, zlib.compress(pickle.dumps(data), level=6), ex=ex)
                return True

    @classmethod
    async def _get_valid_key(cls, key: Dict[str, Any] | str) -> str:
        if isinstance(key, str):
            return key
        elif isinstance(key, Dict[str, Any]):
            return await cls._serialize_key(key)
        raise

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
        key: str | Dict[str, Any],
        many: bool = False,
    ) -> List[T] | T | None:
        valid_key = await cls._get_valid_key(key)
        data = await cls.get_data(key=valid_key)
        match many:
            case True:
                if not isinstance(data, List):
                    raise
                return data

            case False:
                return data
            case _:
                raise

    @classmethod
    async def delete(
        cls,
        key: str | Dict[str, Any],
        cache: Redis = Depends(_get_redis),
    ) -> bool:
        valid_key = await cls._get_valid_key(key)
        await cache.unlink(valid_key)
        return True

    @classmethod
    async def create(
        cls,
        key: str | Dict[str, Any],
        value: T,
        expire: timedelta | int | None,
    ) -> bool:
        valid_key = await cls._get_valid_key(key)
        await cls.set_data(key=valid_key, data=value, ex=expire)

        return True

    @classmethod
    async def update(
        cls,
        key: str | Dict[str, Any],
        value: T,
        expire: timedelta | int | None,
    ) -> bool:
        valid_key = await cls._get_valid_key(key)
        await cls.set_data(key=valid_key, data=value, ex=expire)

        return True
