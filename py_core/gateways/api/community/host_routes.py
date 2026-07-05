from fastapi import (
    Depends,
    HTTPException,
    APIRouter,
)
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from services import HostService
from gateways.api.auth import get_current_user_id

from loguru import logger

router = APIRouter(prefix="/host", route_class=DishkaRoute)


@router.get("/create")
async def get_me(
    host_service: FromDishka[HostService], user_id: str = Depends(get_current_user_id)
):

    try:
        h = await host_service.create(owner_id=user_id)
    except:
        raise HTTPException(status_code=400)

    return h
