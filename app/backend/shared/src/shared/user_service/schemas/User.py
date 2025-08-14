from pydantic import BaseModel, Field
from typing import List


class GetUser(BaseModel):
    ids: List[str] | None = Field(None)
    nicknames: List[str] | None = Field(None)
    gender: str | None = Field(None)
    roles: List[str] | None = Field(None)
    conjuction: bool | None = Field(None)


class CreateUser(BaseModel):
    nickname: str = Field(...)
    gender: str = Field(default="")
