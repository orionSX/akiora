from pydantic import BaseModel
from typing import Literal
from modules.community.enums import Server


class LeagueAccount(BaseModel):
    status: Literal["done", "pending"] = "pending"
    username: str
    tagline: str
    server: Server
    solo_tier: str | None = None
    solo_division: int | None = None
    solo_lp: int | None = None
