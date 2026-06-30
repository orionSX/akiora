from fastapi import (
    FastAPI,
    Request,
    Response,
    Depends,
    HTTPException,
    Cookie,
    APIRouter,
)
from dishka.integrations.fastapi import DishkaRoute, FromDishka, inject
from pydantic import BaseModel
from modules.auth import AuthService
from typing import Optional
from modules.auth import get_current_user_id

router = APIRouter(prefix="/user", route_class=DishkaRoute)


@router.get("/api/profile")
async def profile(user_data: dict = Depends(get_current_user_id)):

    return {
        "user_id": user_data["user_id"],
        "email": user_data["email"],
        "created_at": user_data.get("created_at"),
    }
