from typing import Protocol, Dict, Any, TypeVar, List, Callable, Awaitable
from models.Document import Document
from bson import ObjectId
from abc import abstractmethod
from typing_extensions import runtime_checkable

D = TypeVar("D")


class DataManagerError(Exception):
    def __init__(
        self,
        document: Dict[str, Any] | Document | None = None,
        data_storage: str | None = None,
        details: str | None = None,
    ):
        self.document = document
        self.data_storage = data_storage
        self.details = details or "Failed IO"

        doc_info = f"Document: {document}" if document else ""
        coll_info = f" in storage '{data_storage}'" if data_storage else ""
        message = f"{self.details}{coll_info}. {doc_info}"

        super().__init__(message)

    pass


class ReadFail(DataManagerError):
    pass


class CreateFail(DataManagerError):
    pass


class UpdateFail(DataManagerError):
    pass


class DeleteFail(DataManagerError):
    pass


class BadArgs(DataManagerError):
    pass


@runtime_checkable
class DataManager(Protocol):
    @classmethod
    def _get_data_storage(cls) -> str: ...
    @classmethod
    async def get(
        cls,
        query: Dict[str, Any],
    ) -> List[Dict[str, Any]]: ...
    @classmethod
    async def create(
        cls,
        update_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]: ...
    @classmethod
    async def update(
        cls,
        *,
        query: Dict[str, Any],
        update_data: Dict[str, Any],
    ) -> bool: ...

    @classmethod
    async def delete(
        cls,
        query: Dict[str, Any],
    ) -> bool: ...
