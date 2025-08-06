from db import _get_db
from fastapi import Depends
from pydantic import Field
from typing import Type, TypeVar, Dict, Any, List
from models.CustomBase import CustomBase
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from bson import ObjectId

T = TypeVar("T", bound="Document")


class Document(CustomBase):
    id: str = Field(default="", allias="_id")

    @classmethod
    async def _get_collection(
        cls, db: AsyncIOMotorDatabase = Depends(_get_db)
    ) -> AsyncIOMotorCollection:
        return db[cls.__name__.lower() + "s"]

    @classmethod
    async def create(
        cls: Type[T],
        document: T | Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> T:
        if isinstance(document, cls):
            document = document.model_dump(by_alias=True, exclude={"id"})
        result = await collection.insert_one(document)
        return await cls.get_by_id(result)

    @classmethod
    async def update(
        cls: Type[T],
        query: Dict[str, Any],
        update_data: T | Dict[str, Any],
        upsert: bool = False,
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        if isinstance(update_data, cls):
            update_data = update_data.model_dump(by_alias=True, exclude={"id"})
        result = await collection.update_many(
            query, {"$set": update_data}, upsert=upsert
        )
        return result.modified_count > 0

    @classmethod
    async def get_one(
        cls: Type[T],
        query: Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> T | None:
        data = await collection.find_one(query)
        return cls(**data) if data else None

    @classmethod
    async def get_by_id(
        cls: Type[T],
        id: str,
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> T | None:
        data = await collection.find_one({"_id": ObjectId(id)})
        return cls(**data) if data else None

    @classmethod
    async def get_many(
        cls: Type[T],
        query: Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> List[T]:
        data = [cls(**x) async for x in collection.find(query)]
        return data

    @classmethod
    async def delete_one(
        cls: Type[T],
        query: Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        result = await collection.delete_one(query)
        return result.deleted_count > 0

    @classmethod
    async def delete_by_id(
        cls: Type[T],
        id: str,
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        result = await collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    @classmethod
    async def delete_many(
        cls: Type[T],
        query: Dict[str, Any],
        collection: AsyncIOMotorCollection = Depends(_get_collection),
    ) -> bool:
        """do i need to check length of found docs first?"""
        result = await collection.delete_many(query)
        return result.deleted_count > 0