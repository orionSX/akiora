from pydantic import BaseModel, ConfigDict, Field
from typing import Dict


class Socials(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )

    discord: Dict[str, str] = Field(default_factory=dict)
    telegram: Dict[str, str] = Field(default_factory=dict)
    vkontakte: Dict[str, str] = Field(default_factory=dict)
    youtube: Dict[str, str] = Field(default_factory=dict)
    twitch: Dict[str, str] = Field(default_factory=dict)
    boosty: Dict[str, str] = Field(default_factory=dict)
