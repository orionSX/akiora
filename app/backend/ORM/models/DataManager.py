from typing import Protocol, Dict, Any, TypeVar, List, Callable, Awaitable
from models.Document import Document
from bson import ObjectId
from abc import abstractmethod
from typing_extensions import runtime_checkable

D = TypeVar("D")


class DataManagerError(Exception):
    def __init__(
        self,
        document: Dict[str, Any] | Document = None,
        data_storage: str = None,
        details: str = None,
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
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId],
        many: bool,
        by_id: bool,
        **kwargs,
    ) -> List[D] | D | None: ...
    @classmethod
    async def create(
        cls,
        update_data: D | Dict[str, Any] | List[D] | List[Dict[str, Any]],
        many: bool,
        **kwargs,
    ) -> D | List[D]: ...
    @classmethod
    async def update(
        cls,
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId],
        update_data: D | Dict[str, Any] | List[D] | List[Dict[str, Any]],
        many: bool,
        by_id: bool,
        **kwargs,
    ) -> bool: ...

    @classmethod
    async def delete(
        cls,
        query: str | ObjectId | Dict[str, Any] | List[str | ObjectId],
        many: bool,
        by_id: bool,
        **kwargs,
    ) -> bool: ...


async def manage_crud(
    *,
    data_storage: str,
    many: bool,
    by_id: bool = False,
    query: str | Dict[str, Any] | None = None,
    update_data: Dict[str, Any] | None = None,
    if_many: Callable[..., Awaitable] | None = None,
    if_many_by_id: Callable[..., Awaitable] | None = None,
    if_single: Callable[..., Awaitable] | None = None,
    if_single_by_id: Callable[..., Awaitable] | None = None,
):
    """redis support will be added l8r maybe :p"""

    await _validate_manager(
        data_storage=data_storage,
        many=many,
        by_id=by_id,
        if_many=if_many,
        id_if_many=if_many_by_id,
        if_single=if_single,
        id_if_single=if_single_by_id,
        query=query,
        update_data=update_data,
    )

    kwargs = {
        k: v
        for k, v in [("query", query), ("update_data", update_data)]
        if v is not None
    }

    do_single = if_single(**kwargs) if not by_id else if_single_by_id(**kwargs)
    do_many = if_many(**kwargs) if not by_id else if_many_by_id(**kwargs)

    return await _match(flag=many, do_many=do_many, do_single=do_single)


async def _validate_manager(
    *,
    data_storage: str,
    many: bool,
    by_id: bool,
    if_many,
    id_if_many,
    if_single,
    id_if_single,
    query,
    update_data,
):
    if not (query or update_data):
        raise BadArgs(
            data_storage=data_storage,
            details="Makes no sense to run CRUD without find and create",
        )
    if by_id and not (id_if_many or id_if_single):
        raise BadArgs(
            data_storage=data_storage,
            details="Manager doesnt support id query",
        )
    if many and not (if_many or id_if_many):
        raise BadArgs(
            data_storage=data_storage,
            details="Manager doesnt support many query",
        )
    if not many and not (if_single or id_if_single):
        raise BadArgs(
            data_storage=data_storage,
            details="Manager doesnt support single query",
        )


async def _match(
    *,
    flag: bool,
    do_many: Callable[..., Awaitable],
    do_single: Callable[..., Awaitable],
):
    match flag:
        case True:
            return await do_many
        case False:
            return await do_single
        case _:
            raise BadArgs(details=f"flag should be bool {flag=}")
