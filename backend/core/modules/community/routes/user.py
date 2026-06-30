from fastapi import (
    FastAPI,
    Request,
    Response,
    Depends,
    HTTPException,
    Cookie,
    APIRouter,
)
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from pydantic import BaseModel
from modules.auth import AuthService
from modules.community.services import UserService
from typing import Optional
from modules.auth import get_current_user_id

router = APIRouter(prefix="/user", route_class=DishkaRoute)


@router.get("/me")
async def get_me(
    user_service: FromDishka[UserService], user_id: str = Depends(get_current_user_id)
):
    u = await user_service.get_by_id(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u


@router.patch("/update")
async def patch_user(
    patch: dict,
    user_service: FromDishka[UserService],
    user_id: str = Depends(get_current_user_id),
):
    u = await user_service.update_user(user_id, patch)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u
