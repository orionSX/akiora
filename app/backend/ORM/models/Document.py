from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, List
from abc import abstractmethod


class Document(BaseModel):
    __slots__ = ()
    id: str = Field(default="", alias="_id")
    model_config = ConfigDict(
        validate_by_alias=True,
        validate_by_name=True,
        extra="allow",
    )

    @classmethod
    @abstractmethod
    async def get_find_query(cls, data: BaseModel) -> Dict[str, Any]: ...

    @classmethod
    @abstractmethod
    async def get_update_data(cls, data: BaseModel) -> Dict[str, Any]: ...

    @classmethod
    @abstractmethod
    async def get_create_data(cls, data: BaseModel) -> List[Dict[str, Any]]: ...
