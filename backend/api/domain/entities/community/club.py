from beanie import Document, Indexed
from typing import Annotated
from pydantic import Field
from uuid import UUID, uuid4
from datetime import datetime
from utils import time_now


class Club(Document):
    id: UUID = Field(default_factory=uuid4)
    owner_id: Annotated[UUID, Indexed(unique=True)]
    name: str = Field(min_length=1, max_length=64)
    avatar: str | None = None
    background: str | None = None
    description: str | None = Field(default=None, max_length=500)
    admins: list[UUID] = Field(default_factory=list)
    members: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=time_now)
    pending_requests: list[UUID] = Field(default_factory=list)

    class Settings:
        bson_encoders = {UUID: str}
