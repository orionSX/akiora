from beanie import Document
from pydantic import Field, BaseModel
from uuid import UUID, uuid4
from typing import Literal
from datetime import datetime
from utils import time_now


def default_name():
    return f"user{int(time_now().timestamp())}"


Platform = Literal["tg", "ds"]
Roles = Literal["top", "jungle", "mid", "adc", "support"]


class DraftUnit(BaseModel):
    user_id: UUID
    roles: list[Roles] = Field(default_factory=list, min_length=1, max_length=3)
    tier: int = Field(default=0, ge=0, le=10)


class DraftPreparation(Document):
    id: UUID = Field(default_factory=uuid4)
    tournament_id: UUID
    start_date: datetime
    players: list[DraftUnit] = Field(default_factory=list)
    pending_players: list[DraftUnit] = Field(default_factory=list)
    blocked_players: list[UUID] = Field(default_factory=list)
    is_open: bool = False
    captains: list[DraftUnit] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=time_now)

    class Settings:
        bson_encoders = {UUID: str}


class Tournament(Document):
    id: UUID = Field(default_factory=uuid4)
    host: UUID
    name: str = Field(min_length=1, max_length=64)
    description: str = Field(default="", max_length=500)
    start_date: datetime
    teams: list[UUID] = Field(default_factory=list)
    pending_teams: list[UUID] = Field(default_factory=list)
    is_open: bool = False
    type: Literal["draft", "presign"] = "draft"
    blocked_teams: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=time_now)
    draft_preparation: DraftPreparation | None = None

    class Settings:
        bson_encoders = {UUID: str}
