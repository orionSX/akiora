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


class CRUD(BaseModel):
    """Problems with exception handilng in asyncio.wait"""

    data_managers: List[Type[DataManager]]
    model: Type[Document]
    response_schema: Type[BaseModel] | None = None

    async def get(
        self,
        query: BaseModel,
    ) -> List[BaseModel] | BaseModel | None:
        valid_query = await self.model.get_find_query(query)
        tasks = [
            asyncio_create_task(
                self._get_by_manager(manager=manager, query=valid_query)
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
        create_data: BaseModel,
    ) -> List[BaseModel] | BaseModel | None:
        valid_create_data = await self.model.get_create_data(create_data)

        tasks = [
            asyncio_create_task(
                self._create_by_manager(
                    manager=manager,
                    create_data=valid_create_data,
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
                if result is not None and len(result) > 0:
                    return result

            if not pending:
                return None

            tasks = pending

    async def update(
        self,
        *,
        query: BaseModel,
        update_data: BaseModel,
    ) -> bool:
        valid_query = await self.model.get_find_query(query)
        valid_update_data = await self.model.get_update_data(update_data)
        tasks = [
            asyncio_create_task(
                self._update_by_manager(
                    manager=manager, query=valid_query, update_data=valid_update_data
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
        query: BaseModel,
    ) -> bool:
        valid_query = await self.model.get_find_query(query)
        tasks = [
            asyncio_create_task(
                self._delete_by_manager(manager=manager, query=valid_query)
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
        self, *, manager: type[DataManager], query: Dict[str, Any]
    ) -> List[BaseModel] | BaseModel | None:
        try:
            data = await manager.get(query=query)
            if data:
                if isinstance(data, List):
                    return [self.validate_response(item) for item in data]
                return self.validate_response(data)
            return None

        except Exception:
            return None

    async def _create_by_manager(
        self, manager: Type[DataManager], create_data: List[Dict[str, Any]]
    ) -> List[BaseModel]:
        try:
            data = await manager.create(create_data)
            if data:
                if isinstance(data, List):
                    ld = [self.validate_response(item) for item in data]
                    return ld
                else:
                    return [self.validate_response(data)]
            return []

        except Exception as e:
            print(e)
            return []

    async def _update_by_manager(
        self,
        manager: Type[DataManager],
        query: Dict[str, Any],
        update_data: Dict[str, Any],
    ) -> bool:
        try:
            return await manager.update(query=query, update_data=update_data)

        except Exception:
            return False

    async def _delete_by_manager(
        self,
        *,
        manager: Type[DataManager],
        query: Dict[str, Any],
    ) -> bool:
        try:
            return await manager.delete(query=query)

        except Exception:
            return False

    def validate_response(self, item: Dict[str, Any]) -> BaseModel:
        if self.response_schema:
            return self.response_schema.model_validate(item)
        return self.model.model_validate(item)
