from models.data_managers.MongoManager import MongoManager, T
from models.data_managers.DragonManager import DragonManager
from typing import Type, Dict, Any, List, Generic


from asyncio import (
    create_task as asyncio_create_task,
    wait as asyncio_wait,
    FIRST_COMPLETED as ASYNCIO_FIRST_COMPLETED,
    ALL_COMPLETED as ASYNCIO_ALL_COMPLETED,
)


class DataManager:
    db: Type[MongoManager]
    cache: Type[DragonManager]

    def __init__(self, db: Type[MongoManager], cache: Type[DragonManager]):
        self.db = db
        self.cache = cache

    async def get(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        tasks = [
            asyncio_create_task(self.db.get(query=query), name="db"),
            asyncio_create_task(self.cache.get(query=query), name="cache"),
        ]

        while True:
            done, pending = await asyncio_wait(
                tasks, return_when=ASYNCIO_FIRST_COMPLETED
            )

            for task in done:
                result = task.result()
                source = task.get_name()
                if result:
                    if source == "db":
                        # do i fire background taks here or await idk
                        await self.cache.create(query, result)
                    for t in pending:
                        t.cancel()
                    return result

            if not pending:
                raise

            tasks = pending

    async def create(self, create_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # idk if it makes sense to preventive cache since we cant really predict query
        data = await self.db.create(create_data)
        return data

    async def update(
        self,
        *,
        query: Dict[str, Any],
        update_data: Dict[str, Any],
    ) -> bool:
        tasks = [
            asyncio_create_task(self.db.update(query=query, update_data=update_data)),
            asyncio_create_task(
                self.cache.update(query=query, update_data=update_data)
            ),
        ]

        done, pending = await asyncio_wait(tasks, return_when=ASYNCIO_ALL_COMPLETED)
        res = [task.result() for task in done]
        return all(res)

    async def delete(self, query: Dict[str, Any]):
        tasks = [
            asyncio_create_task(self.db.delete(query=query)),
            asyncio_create_task(self.cache.delete(query=query)),
        ]
        done, pending = await asyncio_wait(tasks, return_when=ASYNCIO_ALL_COMPLETED)
        res = [task.result() for task in done]
        return all(res)


class DataManagerError(Exception):
    def __init__(
        self,
        document: Dict[str, Any] | None = None,
        data_storage: str | None = None,
        details: str | None = None,
    ):
        self.document = document
        self.data_storage = data_storage
        self.details = details or "Failed IO"

        doc_info = f"Document: {document}" if document else ""
        coll_info = f" in storage '{data_storage}'" if data_storage else ""
        message = f"{self.details}{coll_info}. {doc_info}"

        super().__init__(message)

    pass


class ReadFail(DataManagerError):
    pass


class CreateFail(DataManagerError):
    pass


class UpdateFail(DataManagerError):
    pass


class DeleteFail(DataManagerError):
    pass


class BadArgs(DataManagerError):
    pass
