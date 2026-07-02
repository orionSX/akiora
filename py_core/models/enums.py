from enum import Enum


class Server(Enum):
    RU = "ru"
    EUW = "euw"


class HostStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    FROZEN = "frozen"


class Role(Enum):
    TOP = "top"
    JG = "jg"
    MID = "mid"
    ADC = "adc"
    SUP = "sup"


class GameDraft(Enum):
    IRONMAN = "ironman"
    FEARLESS = "fearless"
    CLASSIC = "classic"


class PlayerDraft(Enum):
    LINEAR = "linear"
    SNAKE = "snake"


class GameStatus(Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    FINISHED = "finished"


class TournamentType(Enum):
    PRESIGN = "presign"
    DRAFT = "draft"
