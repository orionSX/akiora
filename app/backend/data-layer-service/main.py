from fastapi import FastAPI
from routers.user_service.main import router as user_service_router
from settings import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(user_service_router)
