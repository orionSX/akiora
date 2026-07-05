from fastapi import (
    Depends,
    HTTPException,
    APIRouter,
)
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from services import TournamentService
from gateways.api.auth import get_current_user_id


router = APIRouter(prefix="/tournament", route_class=DishkaRoute)


@router.post("/create")
async def create(
    patch: dict,
    tournament_service: FromDishka[TournamentService],
    user_id: str = Depends(get_current_user_id),
):

    try:
        h = await tournament_service.create(patch, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return h


@router.get("/all")
async def get_all(
    tournament_service: FromDishka[TournamentService],
):

    h = await tournament_service.get_all()

    return h
