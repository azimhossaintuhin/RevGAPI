from fastapi import APIRouter

from src.routers.Users import User_Routers

router = APIRouter(prefix="/api/v1")

router.include_router(User_Routers.router)
