from db_clients import _get_mongo
from fastapi import Depends
from typing import TypeVar, Dict, Any, List, Type, Generic
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from bson import ObjectId
from models.DataManager import CreateFail, manage_crud, BadArgs
from models.Document import Document
from pydantic import validate_call

T = TypeVar("T", bound=Document)


class MongoManager(Generic[T]):
    _model_class: Type[T]

    @classmethod
    async def get(
        cls,
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId],
        many: bool = False,
        by_id: bool = False,
    ) -> List[T] | T | None:
        return await manage_crud(
            data_storage=cls._get_data_storage(),
            many=many,
            by_id=by_id,
            query=query,
            if_many=cls._get_many,
            if_many_by_id=cls._get_many_by_id,
            if_single=cls._get_one,
            if_single_by_id=cls._get_one_by_id,
        )

    @classmethod
    async def create(
        cls,
        update_data: T | Dict[str, Any] | List[T] | List[Dict[str, Any]],
        many: bool = False,
    ) -> T | List[T]:
        return await manage_crud(
            data_storage=cls._get_data_storage(),
            many=many,
            update_data=update_data,
            if_many=cls._create_many,
            if_single=cls._create_one,
        )

    @classmethod
    async def update(
        cls,
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId],
        update_data: T | Dict[str, Any],
        many: bool = False,
        by_id: bool = False,
    ) -> bool:
        return await manage_crud(
            data_storage=cls._get_data_storage(),
            many=many,
            by_id=by_id,
            query=query,
            update_data=update_data,
            if_many=cls._update_many,
            if_many_by_id=cls._update_many_by_id,
            if_single=cls._update_one,
            if_single_by_id=cls._update_one_by_id,
        )

    @classmethod
    async def delete(
        cls,
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId],
        many: bool = False,
        by_id: bool = False,
    ) -> bool:
        return await manage_crud(
            data_storage=cls._get_data_storage(),
            many=many,
            by_id=by_id,
            query=query,
            if_many=cls._delete_many,
            if_many_by_id=cls._delete_many_by_id,
            if_single_by_id=cls._delete_one_by_id,
            if_single=cls._delete_one,
        )

    @classmethod
    def _get_data_storage(cls) -> str:
        return f"MongoDB : collection = {(cls._model_class.__name__.lower() + 's',)}"

    @classmethod
    async def _get_collection(
        cls,
        db: AsyncIOMotorDatabase = Depends(_get_mongo),
    ) -> AsyncIOMotorCollection:
        if not hasattr(cls, "_model_class"):
            raise RuntimeError("Model class not bound to this manager")
        return db[cls._model_class.__name__.lower() + "s"]

    @classmethod
    @validate_call
    async def _create_many(
        cls,
        update_data: List[T] | List[Dict[str, Any]],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> List[T]:
        for doc in update_data:
            if isinstance(doc, Document):
                doc = doc.model_dump(exclude={"id"})
        result = await collection.insert_many(update_data)
        if result.inserted_ids:
            return await cls._get_many_by_id(result.inserted_id)
        raise CreateFail(
            data_storage=cls._get_data_storage(),
            document=update_data,
            details="MongoDB failed creating many",
        )

    @classmethod
    @validate_call
    async def _create_one(
        cls,
        update_data: T | Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> T:
        if isinstance(update_data, Document):
            update_data = update_data.model_dump(exclude={"id"})
        result = await collection.insert_one(update_data)
        if result.inserted_id:
            return await cls._get_one_by_id(str(result.inserted_id))
        raise CreateFail(
            data_storage=cls._get_data_storage(),
            document=update_data,
            details="MongoDB failed creating one",
        )

    @classmethod
    @validate_call
    async def _update_many(
        cls,
        query: Dict[str, Any],
        update_data: T | Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        if isinstance(update_data, Document):
            update_data = update_data.model_dump(exclude={"id"})
        result = await collection.update_many(query, {"$set": update_data})
        return result.modified_count == result.modified_count

    @classmethod
    @validate_call
    async def _update_many_by_id(
        cls,
        query: List[str | ObjectId],
        update_data: T | Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        query = [x if isinstance(x, ObjectId) else ObjectId(x) for x in query]
        if isinstance(update_data, Document):
            update_data = update_data.model_dump(exclude={"id"})
        result = await collection.update_many(
            {"_id": {"$in": query}}, {"$set": update_data}
        )
        return result.modified_count == result.modified_count

    @classmethod
    @validate_call
    async def _update_one(
        cls,
        query: Dict[str, Any],
        update_data: T | Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        if isinstance(update_data, Document):
            update_data = update_data.model_dump(exclude={"id"})
        result = await collection.update_one(query, {"$set": update_data})
        return result.modified_count == result.modified_count

    @classmethod
    @validate_call
    async def _update_one_by_id(
        cls,
        query: str | ObjectId,
        update_data: T | Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        query = query if isinstance(query, ObjectId) else ObjectId(query)
        if isinstance(update_data, Document):
            update_data = update_data.model_dump(exclude={"id"})
        result = await collection.update_one({"_id": query}, {"$set": update_data})
        return result.modified_count == result.matched_count

    @classmethod
    @validate_call
    async def _get_one(
        cls,
        query: Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> T | None:
        return await collection.find_one(query)

    @classmethod
    @validate_call
    async def _get_one_by_id(
        cls,
        query: str | ObjectId,
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> T | None:
        query = query if isinstance(query, ObjectId) else ObjectId(query)
        return await collection.find_one({"_id": query})

    @classmethod
    @validate_call
    async def _get_many(
        cls,
        query: Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> List[T]:
        return await collection.find(query).to_list()

    @classmethod
    @validate_call
    async def _get_many_by_id(
        cls,
        query: List[str | ObjectId],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> List[T] | None:
        query = [x if isinstance(x, ObjectId) else ObjectId(x) for x in query]

        return await collection.find({"_id": {"$in": query}}).to_list()

    @classmethod
    @validate_call
    async def _delete_one(
        cls,
        query: Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        result = await collection.delete_one(query)
        return result.deleted_count > 0

    @classmethod
    @validate_call
    async def _delete_one_by_id(
        cls,
        query: str | ObjectId,
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        query = query if isinstance(query, ObjectId) else ObjectId(query)
        result = await collection.delete_one({"_id": query})
        return result.deleted_count > 0

    @classmethod
    @validate_call
    async def _delete_many(
        cls,
        query: Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        """do i need to check length of found docs first?"""

        result = await collection.delete_many(query)
        return result.deleted_count > 0

    @classmethod
    @validate_call
    async def _delete_many_by_id(
        cls,
        query: List[str | ObjectId],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        """do i need to check length of found docs first?"""

        query = [x if isinstance(x, ObjectId) else ObjectId(x) for x in query]

        result = await collection.delete_many({"_id": {"$in": query}})

        return result.deleted_count > 0
