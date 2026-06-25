from beanie import Document, Indexed
from pydantic import ConfigDict, Field, EmailStr, field_serializer
from uuid import UUID, uuid4
from typing import Literal, Annotated
from datetime import datetime
from utils import time_now


def default_name():
    return f"user{int(time_now().timestamp())}"


Platform = Literal["tg", "ds"]


class User(Document):
    id: UUID = Field(default_factory=uuid4)
    email: Annotated[EmailStr, Indexed(unique=True)]
    avatar: str | None = None
    bio: str | None = Field(default=None, max_length=500)
    nickname: Annotated[str, Indexed(unique=True)] = Field(default_factory=default_name)
    gender: Literal["male", "female"] | None = None
    socials: dict[Platform, str] | None = None
    created_at: datetime = Field(default_factory=time_now)

    @field_serializer("id")
    def serialize_id(self, id: UUID):
        return str(id)

    @field_serializer("created_at")
    def serialize_ca(self, dt: datetime):
        return dt.isoformat()

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
