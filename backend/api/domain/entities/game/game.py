from beanie import Document, Indexed
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Literal, Annotated
from datetime import datetime, UTC


def time_now():
    return datetime.now(tz=UTC)


def default_name():
    return f"user{int(time_now().timestamp())}"


class Draft(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    picked_champs: list[int] = Field(default_factory=list)
    banned_champs: list[int] = Field(default_factory=list)


class Game(Document):
    id: UUID = Field(default_factory=uuid4)
    team_blue: UUID
    team_red: UUID
    picked_champs: list[int] = Field(default_factory=list)
    banned_champs: list[int] = Field(default_factory=list)

    class Settings:
        bson_encoders = {UUID: str}
