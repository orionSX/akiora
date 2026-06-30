from beanie import Document, Indexed
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


class Game(Document):
    id: UUID = Field(default_factory=uuid7)
    team_blue: UUID
    team_red: UUID
    status: Status
    winner: Optional[UUID]
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
