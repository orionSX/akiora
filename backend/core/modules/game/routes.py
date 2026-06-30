from datetime import datetime
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from modules.auth import get_current_user_id
from modules.community.enums import Server
from modules.game import TournamentService
from modules.game.enums import PlayerDraft, TournamentType

router = APIRouter(prefix="/game", tags=["game"], route_class=DishkaRoute)


class CreateTournamentRequest(BaseModel):
    host_id: UUID
    name: str
    description: str | None = None
    server: Server
    tournament_type: TournamentType
    prizepool: str | None = None
    start_time: datetime
    team_size: int | None = None
    team_max_count: int | None = None
    draft_algorithm: PlayerDraft | None = None


class BracketRequest(BaseModel):
    team_ids: list[UUID]


@router.get("/tournaments")
async def list_tournaments(tournament_service: FromDishka[TournamentService]):
    return await tournament_service.list_tournaments()


@router.get("/tournaments/{tournament_id}")
async def get_tournament(
    tournament_id: UUID, tournament_service: FromDishka[TournamentService]
):
    tournament = await tournament_service.get_by_id(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.post("/tournaments")
async def create_tournament(
    data: CreateTournamentRequest,
    tournament_service: FromDishka[TournamentService],
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await tournament_service.create_tournament(user_id, data.model_dump())
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/tournaments/{tournament_id}")
async def patch_tournament(
    tournament_id: UUID,
    patch: dict,
    tournament_service: FromDishka[TournamentService],
    user_id: str = Depends(get_current_user_id),
):
    try:
        tournament = await tournament_service.update_tournament(
            tournament_id=tournament_id,
            owner_id=user_id,
            patch=patch,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.post("/tournaments/{tournament_id}/brackets/single-elimination")
async def generate_single_elimination_bracket(
    tournament_id: UUID,
    data: BracketRequest,
    tournament_service: FromDishka[TournamentService],
    user_id: str = Depends(get_current_user_id),
):
    try:
        tournament = await tournament_service.generate_single_elim_bracket(
            tournament_id=tournament_id,
            owner_id=user_id,
            team_ids=data.team_ids,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament
