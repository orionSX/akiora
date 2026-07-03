from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from models.enums import (
    Server,
    TournamentType,
    PlayerDraft,
    VerificationRequest,
    BracketType,
)
from datetime import datetime


class LeagueAccount(BaseModel):
    status: VerificationRequest = Field(default=VerificationRequest.PENDING)
    username: str
    tagline: str
    server: Server
    solo_tier: Optional[str] = None
    solo_division: Optional[int] = None
    solo_lp: Optional[int] = None
    model_config = ConfigDict(extra="ignore")


class DraftSettings(BaseModel):
    draft_algorithm: PlayerDraft = Field(Default=PlayerDraft.LINEAR)
    captain_pick_time_sec: int = Field(default=60 * 10, ge=60 * 10, le=60 * 30)
    model_config = ConfigDict(extra="ignore")


class PresingSettings(BaseModel):
    team_limit: int = Field(ge=2)
    model_config = ConfigDict(extra="ignore")


class CommonSettings(BaseModel):
    tournament_type: TournamentType
    is_registration_open: bool = True
    starts_at: datetime
    name: str
    server: Server
    description: Optional[str] = None
    prizepool: Optional[str] = None
    bracket_type: BracketType
    team_size: int = Field(ge=1, le=7)
    model_config = ConfigDict(extra="ignore")


class TournamentSettings(BaseModel):
    common_settings: CommonSettings
    presign_settings: Optional[PresingSettings] = None
    draft_settings: Optional[DraftSettings] = None
    model_config = ConfigDict(extra="ignore")
