from asyncio import (
    create_task as asyncio_create_task,
    wait as asyncio_wait,
    FIRST_COMPLETED as ASYNCIO_FIRST_COMPLETED,
    ALL_COMPLETED as ASYNCIO_ALL_COMPLETED,
)
from typing import List, Dict, Any, Type
from pydantic import BaseModel
from models.Document import Document
from models.DataManager import DataManager
from bson import ObjectId


class CRUD(BaseModel):
    """Problems with exception handilng in asyncio.wait"""

    data_managers: List[Type[DataManager]]
    model: Type[Document]

    async def get(
        self,
        *,
        query: BaseModel,
        many: bool = False,
        by_id: bool = False,
    ) -> List[Document] | Document | None:
        query = query.model_dump(exclude_none=True)
        tasks = [
            asyncio_create_task(
                self._get_by_manager(
                    manager=manager, query=query, many=many, by_id=by_id
                )
            )
            for manager in self.data_managers
        ]

        while True:
            done, pending = await asyncio_wait(
                tasks, return_when=ASYNCIO_FIRST_COMPLETED
            )

            for task in done:
                result = task.result()
                if result is not None:
                    for t in pending:
                        t.cancel()
                    return result

            if not pending:
                return None

            tasks = pending

    async def create(
        self,
        *,
        update_data: Document | Dict[str, Any] | List[Document] | List[Dict[str, Any]],
        many: bool,
    ) -> List[Document] | Document | None:
        tasks = [
            asyncio_create_task(
                self._create_by_manager(
                    manager=manager, update_data=update_data, many=many
                )
            )
            for manager in self.data_managers
        ]
        while True:
            done, pending = await asyncio_wait(
                tasks, return_when=ASYNCIO_FIRST_COMPLETED
            )

            for task in done:
                result = task.result()
                if result is not None:
                    return result

            if not pending:
                return None

            tasks = pending

    async def update(
        self,
        *,
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId] = {},
        update_data: Document | Dict[str, Any] | List[Document] | List[Dict[str, Any]],
        many: bool,
        by_id: bool,
    ) -> bool:
        tasks = [
            asyncio_create_task(
                self._update_by_manager(
                    manager=manager,
                    query=query,
                    update_data=update_data,
                    many=many,
                    by_id=by_id,
                )
            )
            for manager in self.data_managers
        ]

        done, pending = await asyncio_wait(tasks, return_when=ASYNCIO_ALL_COMPLETED)
        res: List[bool] = []
        for task in done:
            result = task.result()
            res.append(result)
        return all(res)

    async def delete(
        self,
        *,
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId] = {},
        many: bool = False,
        by_id: bool = False,
    ) -> bool:
        tasks = [
            asyncio_create_task(
                self._delete_by_manager(
                    manager=manager, query=query, many=many, by_id=by_id
                )
            )
            for manager in self.data_managers
        ]

        done, pending = await asyncio_wait(tasks, return_when=ASYNCIO_ALL_COMPLETED)
        res: List[bool] = []
        for task in done:
            result = task.result()
            res.append(result)
        return all(res)

    async def _get_by_manager(
        self, *, manager: DataManager, query, many: bool, by_id: bool
    ) -> List[Document] | Document | None:
        try:
            data = await manager.get(query=query, many=many, by_id=by_id)
            if data:
                if isinstance(data, List):
                    return [self.model.model_validate(item) for item in data]
                return self.model.model_validate(data)
            return None

        except Exception:
            return None

    async def _create_by_manager(
        self, manager: DataManager, update_data, many: bool
    ) -> List[Document] | Document | None:
        try:
            data = await manager.create(update_data=update_data, many=many)
            if data:
                if isinstance(data, List):
                    return [self.model.model_validate(item) for item in data]
                return self.model.model_validate(data)
            return None

        except Exception:
            return None

    async def _update_by_manager(
        self, manager: DataManager, query, update_data, many: bool, by_id: bool
    ) -> bool:
        try:
            return await manager.update(
                query=query, update_data=update_data, many=many, by_id=by_id
            )

        except Exception:
            return False

    async def _delete_by_manager(
        self, *, manager: DataManager, query, many: bool, by_id: bool
    ) -> bool:
        try:
            return await manager.delete(query=query, many=many, by_id=by_id)

        except Exception:
            return False
