from db_clients import _get_mongo
from typing import TypeVar, Dict, Any, List, Type, Generic
from bson import ObjectId
from shared.base.Document import Document


T = TypeVar("T", bound=Document)


# TODO : raise exceptions from datamanager


class MongoManager(Generic[T]):
    _model_class: Type[T]

    @classmethod
    async def _get_collection(
        cls,
    ):
        if not hasattr(cls, "_model_class"):
            raise RuntimeError("Model class not bound to this manager")
        return _get_mongo(f"{cls._model_class.__name__.lower()}s")

    @classmethod
    async def get(cls, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        collection = await cls._get_collection()
        return await collection.find(query).to_list()

    @classmethod
    async def create(
        cls,
        create_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        collection = await cls._get_collection()
        result = await collection.insert_many(create_data)
        if result.inserted_ids:
            t = await cls._get_many_by_id(result.inserted_ids, collection)
            return t
        return []

    @classmethod
    async def update(
        cls,
        *,
        query: Dict[str, Any],
        update_data: Dict[str, Any],
    ) -> bool:
        collection = await cls._get_collection()
        result = await collection.update_many(query, {"$set": update_data})
        return result.modified_count > 0

    @classmethod
    async def delete(
        cls,
        query: Dict[str, Any],
    ) -> bool:
        """Should i check for found amount first?"""
        collection = await cls._get_collection()
        result = await collection.delete_many(query)
        return result.deleted_count > 0

    @classmethod
    def _get_data_storage(cls) -> str:
        return f"MongoDB : collection = {(cls._model_class.__name__.lower() + 's',)}"

    @classmethod
    async def _get_many_by_id(
        cls,
        query: List[ObjectId],
        collection,
    ) -> List[Dict[str, Any]]:
        return await collection.find({"_id": {"$in": query}}).to_list()
