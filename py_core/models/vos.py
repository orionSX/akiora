from pydantic import BaseModel
from typing import Literal, Optional
from models.enums import Server


class LeagueAccount(BaseModel):
    status: Literal["verified", "pending"] = "pending"
    username: str
    tagline: str
    server: Server
    solo_tier: Optional[str] = None
    solo_division: Optional[int] = None
    solo_lp: Optional[int] = None
