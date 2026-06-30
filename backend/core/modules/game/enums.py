from enum import Enum


class GameDraft(Enum):
    IRONMAN = "ironman"
    FEARLESS = "fearless"
    CLASSIC = "classic"


class PlayerDraft(Enum):
    LINEAR = "linear"
    SNAKE = "snake"


class Status(Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    FINISHED = "finished"


class TournamentType(Enum):
    PRESIGN = "presign"
    DRAFT = "draft"
