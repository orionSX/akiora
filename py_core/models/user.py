from beanie import Document, Indexed
from pydantic import ConfigDict, Field, EmailStr, field_serializer, model_validator
from uuid import UUID, uuid7
from typing import Optional, Annotated
from datetime import datetime
from models.vos import LeagueAccount
from utils.helpers import time_now


class User(Document):
    id: UUID = Field(default_factory=uuid7)
    email: Annotated[EmailStr, Indexed(unique=True)]
    avatar_url: Optional[str] = None
    about: Optional[str] = Field(default=None, max_length=500)
    nickname: Annotated[Optional[str], Indexed(unique=True)] = Field(
        default=None, max_length=500
    )
    league_accounts: list[LeagueAccount] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    @field_serializer("id", when_used="json-unless-none")
    def serialize_id(self, id: UUID):
        return str(id)

    @field_serializer("created_at", when_used="json-unless-none")
    def serialize_ca(self, dt: datetime):
        return dt.isoformat()

    @field_serializer("updated_at", when_used="json-unless-none")
    def serialize_ua(self, dt: datetime):
        return dt.isoformat()

    @model_validator(mode="after")
    def set_nickname(self):
        if self.nickname is None:
            self.nickname = self.email
        return self

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
