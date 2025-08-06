from typing import Protocol, Dict, Any, TypeVar, List

D = TypeVar("D", bound="DataManager")


class DataManager(Protocol):
    @classmethod
    async def get(
        cls, find_query: str | Dict[str, Any], many: bool
    ) -> List[D] | D | None: ...
    @classmethod
    async def create(cls, create_query: D | Dict[str, Any]) -> D: ...
    @classmethod
    async def update(
        cls,
        find_query: str | Dict[str, Any],
        update_query: D | Dict[str, Any],
    ) -> bool: ...

    @classmethod
    async def delete(find_query: str | Dict[str, Any], many: bool) -> bool: ...
