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

router = APIRouter(prefix="/auth", route_class=DishkaRoute)


class EmailRequest(BaseModel):
    email: str


class VerifyRequest(BaseModel):
    token: str
    code: str


@router.post("/email/request")
async def request_verification(
    data: EmailRequest, auth_service: FromDishka[AuthService]
):

    token = await auth_service.request_verification(data.email)

    return {
        "message": "Verification code sent to email",
        "token": token,
        "expires_in": 300,
    }


@router.post("/email/verify")
async def verify_code(
    data: VerifyRequest, response: Response, auth_service: FromDishka[AuthService]
):

    result = await auth_service.verify_code_and_create_session(
        token=data.token, code=data.code
    )

    if not result:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    response.set_cookie(
        key="session_token",
        value=result["session_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )

    return Response(status_code=200)


@inject
async def get_current_user_id(
    auth_service: FromDishka[AuthService], session_token: Optional[str] = Cookie(None)
) -> str:

    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_data = await auth_service.verify_cookie_token(session_token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    return user_data.get("user_id")
