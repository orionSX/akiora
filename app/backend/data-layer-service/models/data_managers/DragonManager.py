from db_clients import DragonClient
from typing import Dict, Any, List, TypeVar, Generic, Type
import pickle
import zlib
from shared.base.Document import Document
from settings import CACHE_EXPIRE_TIME

T = TypeVar("T", bound=Document)


class DragonManager(Generic[T]):
    _model_class: Type[T]

    @classmethod
    def _get_data_storage(cls) -> str:
        return f"Dragon : = {(cls._model_class.__name__.lower() + 's',)}"

    @classmethod
    async def get_data(cls, key: str) -> List[Dict[str, Any]]:
        cache = DragonClient.get_client()
        raw_data = await cache.get(key)
        if raw_data:
            decompressed_data = zlib.decompress(raw_data)
            return pickle.loads(decompressed_data)
        return []

    @classmethod
    async def set_data(
        cls,
        key: str,
        data: List[Dict[str, Any]] | Dict[str, Any],
    ) -> bool:
        cache = DragonClient.get_client()
        pickled_data = pickle.dumps(data)
        compressed_data = zlib.compress(pickled_data, level=6)
        await cache.set(key, compressed_data, ex=CACHE_EXPIRE_TIME)
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
    ) -> bool:
        cache = DragonClient.get_client()
        valid_key = await cls._get_valid_key(query)
        await cache.unlink(valid_key)
        return True

    @classmethod
    async def create(
        cls,
        key: Dict[str, Any],
        create_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        valid_key = await cls._get_valid_key(key)
        await cls.set_data(key=valid_key, data=create_data)
        return []

    @classmethod
    async def update(
        cls,
        *,
        query: Dict[str, Any],
        update_data: Dict[str, Any],
    ) -> bool:
        valid_key = await cls._get_valid_key(query)
        await cls.set_data(key=valid_key, data=update_data)
        return True
