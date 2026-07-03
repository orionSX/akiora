from beanie import Document
from pydantic import (
    ConfigDict,
    Field,
)
from uuid import UUID, uuid7
from typing import Optional
from datetime import datetime
from utils.helpers import time_now


class Team(Document):
    id: UUID = Field(default_factory=uuid7)
    name: Optional[str] = None
    captain_id: UUID
    avatar_url: Optional[str] = None
    members: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
