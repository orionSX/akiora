from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Dict, Any, List, Sequence
from abc import abstractmethod
from bson import ObjectId


class Document(BaseModel):
    __slots__ = ()
    id: str = Field(default="", alias="_id")
    model_config = ConfigDict(
        validate_by_alias=True,
        validate_by_name=True,
        extra="allow",
    )

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @classmethod
    @abstractmethod
    async def get_find_query(cls, data: BaseModel) -> Dict[str, Any]: ...

    @classmethod
    @abstractmethod
    async def get_update_data(cls, data: BaseModel) -> Dict[str, Any]: ...

    @classmethod
    @abstractmethod
    async def get_create_data(
        cls, data: Sequence[BaseModel]
    ) -> List[Dict[str, Any]]: ...
