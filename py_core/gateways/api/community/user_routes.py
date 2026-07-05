from fastapi import (
    Depends,
    HTTPException,
    APIRouter,
)
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from services import UserService
from gateways.api.auth import get_current_user_id
from loguru import logger

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
    logger.info(patch)
    try:
        u = await user_service.update(user_id, patch)
    except:
        raise HTTPException(status_code=400)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u
