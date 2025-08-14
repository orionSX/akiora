from typing import List, Dict, Any, Type, Sequence
from pydantic import BaseModel
from shared.base.Document import Document
from models.DataManager import CreateFail, ReadFail, UpdateFail, DeleteFail, DataManager


class CRUD:
    data_manager: DataManager
    model: Type[Document]
    response_schema: Type[BaseModel] | None = None

    def __init__(
        self,
        data_manager: DataManager,
        model: Type[Document],
        response_schema: Type[BaseModel] | None = None,
    ):
        self.data_manager = data_manager
        self.model = model
        self.response_schema = response_schema

    async def get(
        self,
        query: BaseModel,
    ) -> List[BaseModel]:
        try:
            valid_query = await self.model.get_find_query(query)
            return self.validate_response(
                await self.data_manager.get(query=valid_query)
            )
        except Exception as e:
            raise ReadFail

    async def create(
        self,
        create_data: Sequence[BaseModel],
    ) -> List[BaseModel]:
        try:
            valid_create_data = await self.model.get_create_data(create_data)
            return self.validate_response(
                await self.data_manager.create(create_data=valid_create_data)
            )
        except Exception:
            raise CreateFail

    async def update(
        self,
        *,
        query: BaseModel,
        update_data: BaseModel,
    ) -> bool:
        try:
            valid_query = await self.model.get_find_query(query)
            valid_update_data = await self.model.get_update_data(update_data)
            return await self.data_manager.update(
                query=valid_query, update_data=valid_update_data
            )
        except Exception:
            raise UpdateFail

    async def delete(
        self,
        query: BaseModel,
    ) -> bool:
        try:
            valid_query = await self.model.get_find_query(query)
            return await self.data_manager.delete(query=valid_query)
        except Exception:
            raise DeleteFail

    def validate_response(self, items: List[Dict[str, Any]]) -> List[BaseModel]:
        # do i need to sep return to single | list | none?
        if self.response_schema:
            return [self.response_schema.model_validate(x) for x in items]
        return [self.model.model_validate(x) for x in items]
