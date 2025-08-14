from fastapi import APIRouter
from routers.user_service.user import router as user_router

router = APIRouter(prefix="/user_service", tags=["UserService Route"])

router.include_router(user_router)
