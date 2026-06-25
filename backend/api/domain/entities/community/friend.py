from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from enum import Enum


class FriendStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DENIED = "denied"


class Friend(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id_1: UUID
    user_id_2: UUID
    status: FriendStatus = FriendStatus.PENDING

    class Settings:
        bson_encoders = {UUID: str}
