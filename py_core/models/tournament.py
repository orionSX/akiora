from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID, uuid7

from beanie import Document, Indexed
from pydantic import ConfigDict, Field, field_serializer, BaseModel


from models.enums import PlayerDraft, GameStatus, TournamentType, Server
from utils.helpers import time_now


class Bracket(BaseModel):
    pass


class Tournament(Document):
    id: UUID = Field(default_factory=uuid7)
    host_id: Annotated[UUID, Indexed()]
    name: str = Field(min_length=1, max_length=64)
    description: Optional[str] = Field(default=None, max_length=2000)
    server: Server
    tournament_type: TournamentType
    status: GameStatus = GameStatus.SCHEDULED
    prizepool: Optional[str] = Field(default=None, max_length=256)
    starts_at: datetime
    draft_starts_at: Optional[datetime] = None
    team_size: Optional[int] = Field(default=None, ge=1, le=7)
    team_max_count: Optional[int] = Field(default=None, ge=2, le=512)
    draft_algorithm: Optional[PlayerDraft] = None
    bracket: Optional[dict] = None
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    @field_serializer("id", "host_id", when_used="json-unless-none")
    def serialize_uuid(self, value: UUID):
        return str(value)

    @field_serializer(
        "created_at",
        "updated_at",
        "draft_starts_at",
        "starts_at",
        when_used="json-unless-none",
    )
    def serialize_datetime(self, value: datetime):
        return value.isoformat()

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
