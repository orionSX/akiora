from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID, uuid7

from beanie import Document, Indexed
from pydantic import ConfigDict, Field, field_serializer, BaseModel
from models.vos import TournamentSettings, EloCard
from models.bracket import Bracket
from models.enums import GameStatus, Role, PoolStatus
from utils.helpers import time_now


class TeamJoinRequest(BaseModel):
    team_id: UUID
    created_at: datetime = Field(default_factory=time_now)


class PlayerJoinRequest(BaseModel):
    user_id: UUID
    main_role: Role
    secondary_role: Optional[Role] = None
    created_at: datetime = Field(default_factory=time_now)


class PoolItem(BaseModel):
    player: Optional[PlayerJoinRequest] = None
    team: Optional[TeamJoinRequest] = None
    elo_card: EloCard


class Team(BaseModel):
    id: UUID = Field(default_factory=uuid7)
    name: Optional[str] = None
    captain_id: UUID
    avatar_url: Optional[str] = None
    members: list[PoolItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}


class TournamentPool(BaseModel):
    pending_requests: list[TeamJoinRequest | PlayerJoinRequest] = Field(
        default_factory=list
    )
    accepted_requests: list[TeamJoinRequest | PlayerJoinRequest] = Field(
        default_factory=list
    )
    blocked_users: list[UUID] = Field(default_factory=list)
    captains: Optional[list[UUID]] = None
    pool: list[PoolItem] = Field(default_factory=list)
    teams: list[Team] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)
    status: PoolStatus = PoolStatus.OPENED
    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}

    def add_pending_user(self, patch: dict):
        if self.status == PoolStatus.CLOSED:
            raise
        pjr = PlayerJoinRequest(**patch)
        if pjr.user_id not in [
            x.user_id for x in (self.pending_requests + self.accepted_requests)
        ]:
            self.pending_requests.append(pjr)

    def add_accepted_user(self, player_id: UUID, elo_card: EloCard):
        if self.status == PoolStatus.CLOSED:
            raise

        req = next(x for x in self.pending_requests if x.user_id == player_id)
        if req not in self.accepted_requests:
            self.accepted_requests.append(req)
            self.pending_requests.remove(req)
            pi = PoolItem(player=req, elo_card=elo_card)
            self.pool.append(pi)

    def patch_captains(self, remove: list[UUID], append: list[UUID]):
        self.teams = [y for y in self.teams if y.captain_id not in remove]
        self.captains = [x for x in self.captains if x not in remove]
        for x in append:
            if x not in self.captains:
                self.teams.append(Team(captain_id=x))
                self.captains.append(x)

    def add_to_team(self, player_id: UUID, captain_id: UUID):
        plr = next(x for x in self.pool if x.player.user_id == player_id)
        team = next(x for x in self.teams if x.captain_id == captain_id)
        team.members.append(plr)
        self.pool.remove(plr)

    def update_pool_player(self, player_id: str, patch: dict):

        pc = next((x for x in self.pool if str(x.player.user_id) == player_id), None)
        if pc:
            elocard = EloCard(**patch)
            pc.elo_card = elocard


class Tournament(Document):
    id: UUID = Field(default_factory=uuid7)
    host_id: Annotated[UUID, Indexed()]
    settings: TournamentSettings
    status: GameStatus = GameStatus.SCHEDULED
    bracket: Optional[Bracket] = None
    pool: TournamentPool = Field(default_factory=TournamentPool)
    created_at: datetime = Field(default_factory=time_now)
    updated_at: datetime = Field(default_factory=time_now)

    @field_serializer("id", "host_id", when_used="json-unless-none")
    def serialize_uuid(self, value: UUID):
        return str(value)

    @field_serializer(
        "created_at",
        "updated_at",
        when_used="json-unless-none",
    )
    def serialize_datetime(self, value: datetime):
        return value.isoformat()

    model_config = ConfigDict(extra="ignore")

    class Settings:
        bson_encoders = {UUID: str}
