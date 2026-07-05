from fastapi import Response, HTTPException, Cookie, APIRouter, Depends
from dishka.integrations.fastapi import DishkaRoute, FromDishka, inject

from services import HostService
from typing import Optional
from gateways.api.auth.schemas import EmailRequest, VerifyRequest
from loguru import logger

router = APIRouter(prefix="/admin", route_class=DishkaRoute)


@router.patch("/host/{id}")
async def request_verification(
    id: str, patch: dict, host_service: FromDishka[HostService]
):

    logger.info(patch)
    logger.info(id)
    h = await host_service.update(id, patch)

    return h
