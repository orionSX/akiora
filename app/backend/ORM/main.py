from setup import app
from routers.user_service.main import router as user_service_router

app.include_router(user_service_router)
