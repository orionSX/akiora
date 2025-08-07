from pydantic import BaseModel, ConfigDict, Field


class Document(BaseModel):
    __slots__ = ()
    id: str = Field(default="", alias="_id")
    model_config = ConfigDict(
        validate_by_alias=True,
        validate_by_name=True,
        extra="allow",
    )
