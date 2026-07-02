from beanie import Document
from pydantic import (
    ConfigDict,
    Field,
)
from uuid import UUID, uuid7
from typing import Optional
from datetime import datetime
from utils.helpers import time_now
from models.enums import GameStatus


class Game(Document):
    id: UUID = Field(default_factory=uuid7)
    team_blue: UUID
    team_red: UUID
    status: GameStatus = Field(default=GameStatus.SCHEDULED)
    game_result_rofl_url: Optional[str] = None
    winner: Optional[UUID] = None
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
