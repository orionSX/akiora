from fastapi import APIRouter, HTTPException, Query
from helpers.CRUD_instances import user_crud
from schemas.user_service.user import CreateUser, GetUser
from typing import Annotated

router = APIRouter(prefix="/users", tags=["UserService Route"])


@router.get("/")
async def get_all_users(query: Annotated[GetUser, Query()]):
    if users := await user_crud.get(query):
        return users
    raise HTTPException(status_code=404)


@router.post("/")
async def create_user():
    if users := await user_crud.create({"name": "Alex"}):
        return users
    raise HTTPException(status_code=400)
