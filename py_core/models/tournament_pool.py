from beanie import Document
from pydantic import ConfigDict, Field, BaseModel
from uuid import UUID, uuid7
from typing import Optional
from datetime import datetime
from utils.helpers import time_now
from models.enums import Role


class TeamJoinRequest(BaseModel):
    team_id: UUID
    created_at: datetime = Field(default_factory=time_now)


class PlayerJoinRequest(BaseModel):
    user_id: UUID
    main_role: Role
    secondary_role: Optional[Role] = None
    created_at: datetime = Field(default_factory=time_now)


class PlayerCard(BaseModel):
    user_id: UUID
    main_role: Role
    secondary_role: Optional[Role] = None
    elo: int = Field(default=0, ge=0)


class TeamCard(BaseModel):
    team_id: UUID
    main_role: Role
    elo: int = Field(default=0, ge=0)


class TournamentPool(Document):
    id: UUID = Field(default_factory=uuid7)
    tournament_id: UUID
    pending_requests: list[TeamJoinRequest | PlayerJoinRequest] = Field(
        default_factory=list
    )
    accepted_requests: list[TeamJoinRequest | PlayerJoinRequest] = Field(
        default_factory=list
    )
    pool: list[TeamCard | PlayerCard] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
