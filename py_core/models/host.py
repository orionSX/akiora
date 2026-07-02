from beanie import Document, Indexed
from pydantic import (
    ConfigDict,
    Field,
    field_serializer,
)
from uuid import UUID, uuid7
from typing import Optional, Annotated
from datetime import datetime
from utils.helpers import time_now


class Host(Document):
    id: UUID = Field(default_factory=uuid7)
    owner_id: Annotated[UUID, Indexed(unique=True)]
    avatar_url: Optional[str] = None
    about: Optional[str] = Field(default=None, max_length=500)
    nickname: Annotated[Optional[str], Indexed(unique=True)] = Field(
        default=None, max_length=500
    )
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    @field_serializer("id", when_used="json-unless-none")
    def serialize_id(self, id: UUID):
        return str(id)

    @field_serializer("owner_id", when_used="json-unless-none")
    def serialize_owner_id(self, id: UUID):
        return str(id)

    @field_serializer("created_at", when_used="json-unless-none")
    def serialize_ca(self, dt: datetime):
        return dt.isoformat()

    @field_serializer("updated_at", when_used="json-unless-none")
    def serialize_ua(self, dt: datetime):
        return dt.isoformat()

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
