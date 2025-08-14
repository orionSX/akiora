from fastapi import APIRouter, HTTPException, Query, Body
from helpers.CRUD_instances import user_crud
from shared.user_service.schemas.User import CreateUser, GetUser
from typing import Annotated, Sequence

router = APIRouter(prefix="/users", tags=["UserService Route"])


@router.get("/")
async def get_all_users(query: Annotated[GetUser, Query()]):
    if users := await user_crud.get(query=query):
        return users
    raise HTTPException(status_code=404)


@router.post("/")
async def create_users(
    create_data: Annotated[Sequence[CreateUser], Body()],
):  # Sequence cus Lists are invariant (List[child] != List[papa]
    if users := await user_crud.create(create_data=create_data):
        return users
    raise HTTPException(status_code=422)
