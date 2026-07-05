from beanie import Document, Indexed
from pydantic import (
    ConfigDict,
    Field,
)
from uuid import UUID, uuid7
from typing import Optional, Annotated
from datetime import datetime
from utils.helpers import time_now
from models.enums import GameStatus
from models.game import Game


class Match(Document):
    id: UUID = Field(default_factory=uuid7)
    team1: UUID
    team2: UUID
    status: GameStatus = Field(default=GameStatus.SCHEDULED)
    tournament_id: Annotated[UUID, Indexed()]
    winner: Optional[UUID] = None
    games: list[Game] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
