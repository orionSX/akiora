from beanie import Document, Indexed, Link
from pydantic import (
    ConfigDict,
    Field,
    field_serializer,
    model_validator,
)
from uuid import UUID, uuid7
from typing import Optional, Annotated
from datetime import datetime
from modules.utils import time_now
from modules.game.enums import Status
from modules.game.models.game import Game


class Match(Document):
    id: UUID = Field(default_factory=uuid7)
    team1: UUID
    team2: UUID
    status: Status
    tournament_id: Annotated[UUID, Indexed()]
    winner: Optional[UUID]
    games: list[Link[Game]]
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
