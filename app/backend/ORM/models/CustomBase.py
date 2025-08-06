from pydantic import BaseModel, ConfigDict


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CustomBase(BaseModel):
    __slots__ = ()
    model_config = ConfigDict(
        alias_generator=_to_camel, populate_by_name=True, extra="ignore"
    )
