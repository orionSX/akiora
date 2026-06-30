from enum import Enum


class Server(Enum):
    RU = "ru"
    EUW = "euw"


class Status(Enum):
    PENDING = "pending"
    DONE = "done"
    REJECTED = "rejected"


class Role(Enum):
    TOP = "top"
    JG = "jg"
    MID = "mid"
    ADC = "adc"
    SUP = "sup"
