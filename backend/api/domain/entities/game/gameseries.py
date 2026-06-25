from beanie import Document, Indexed
from pydantic import Field
from uuid import UUID, uuid4
from typing import Literal, Annotated
from datetime import datetime, UTC


def time_now():
    return datetime.now(tz=UTC)


def default_name():
    return f"user{int(time_now().timestamp())}"


Platform = Literal["tg", "ds"]


class GameSeries(Document):
    id: UUID = Field(default_factory=uuid4)
    team1: UUID
    team2: UUID
    

    class Settings:
        bson_encoders = {UUID: str}
