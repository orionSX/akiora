from beanie import Document, Indexed
from pydantic import Field
from uuid import UUID, uuid4
from typing import Literal, Annotated
from datetime import datetime, UTC


def time_now():
    return datetime.now(tz=UTC)


def default_name():
    return f"user{int(time_now().timestamp())}"


Platform = Literal["tg", "ds"]


class LeagueAccount(Document):
    id: UUID = Field(default_factory=uuid4)
    status: Literal["done", "pending"] = "pending"
    nickname: Annotated[str, Indexed(unique=True)]
    username: str
    tagline: str
    server: str
    profile_image_url: str | None = None
    solo_tier: str | None = None
    solo_division: int | None = None
    solo_lp: int | None = None
    solo_tier_image_url: str | None = None
    user_id: UUID

    class Settings:
        bson_encoders = {UUID: str}
