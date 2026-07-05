from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from models.enums import (
    Server,
    TournamentType,
    PlayerDraft,
    VerificationRequest,
    BracketType,
)
from datetime import datetime
from math import exp

TIER_GRADE: dict[Any, int] = {
    "challenger": 10,
    "grandmaster": 9,
    "master": 8,
    "diamond": 7,
    "emerald": 6,
    "platinum": 5,
    "gold": 4,
    "silver": 3,
    "bronze": 2,
    "iron": 1,
    None: 0,
}


class LeagueAccount(BaseModel):
    status: VerificationRequest = Field(default=VerificationRequest.PENDING)
    username: str
    tagline: str
    server: Server
    solo_tier: Optional[str] = None
    solo_division: int = 4
    solo_lp: int = 0
    model_config = ConfigDict(extra="ignore")

    @property
    def tier(self) -> int:
        """Server sensitive"""
        if self.server == Server.RU:
            return min(8, TIER_GRADE[self.solo_tier])
        return TIER_GRADE[self.solo_tier]

    @property
    def elo(self) -> int:
        """Tier insensitive"""

        val = 100 * (4 - self.solo_division) + self.solo_lp
        if self.server == Server.RU and self.tier >= 8:
            return val / 2

        return val

    def get_best(cls, left: LeagueAccount, right: LeagueAccount) -> LeagueAccount:
        """Server insensitive"""
        if left.solo_tier is None:
            return right
        if right.solo_tier is None:
            return left
        if left.solo_tier == right.solo_tier:
            return left._get_best_same_tier(right)
        else:
            if TIER_GRADE[left.solo_tier] > TIER_GRADE[right.solo_tier]:
                return left
            else:
                return right

    def _get_best_same_tier(self, other: LeagueAccount) -> LeagueAccount:
        if self.solo_division == other.solo_division:
            if self.solo_lp - other.solo_lp >= 0:
                return self
            else:
                return other
        elif self.solo_division > other.solo_division:
            return self
        else:
            return other


class DraftSettings(BaseModel):
    draft_algorithm: PlayerDraft = Field(default=PlayerDraft.LINEAR)
    captain_pick_time_sec: int = Field(default=60 * 10, ge=60 * 10, le=60 * 30)
    draft_starts_at: datetime
    model_config = ConfigDict(extra="ignore")


class PresingSettings(BaseModel):
    max_team_count: int = Field(ge=2)
    model_config = ConfigDict(extra="ignore")


class CommonSettings(BaseModel):
    tournament_type: TournamentType
    is_registration_open: bool = True
    starts_at: datetime
    name: str
    server: Server
    about: Optional[str] = None
    prizepool: str = None
    bracket_type: BracketType
    team_size: int = Field(default=5, ge=1, le=7)
    model_config = ConfigDict(extra="ignore")


class TournamentSettings(BaseModel):
    common_settings: CommonSettings
    presign_settings: Optional[PresingSettings] = None
    draft_settings: Optional[DraftSettings] = None
    model_config = ConfigDict(extra="ignore")


class EloCard(BaseModel):
    tier: int = 0
    value: int = 0

    @property
    def total(self) -> int:
        return self.tier * self.value
