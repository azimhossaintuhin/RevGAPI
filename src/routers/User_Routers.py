from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from src.dependencies.get_user import CurrentUserID
from src.schemas.User import UserCreate, UserOutput, UserLoginOutput, UserLogin, UserUpdate
from src.services.Users import user_service





router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create", response_model=UserOutput)
async def create_user(user: UserCreate, service: user_service) -> UserOutput:
    return await service.create_user(user)


@router.post("/login", response_model=UserLoginOutput)
async def login_user(
    service: user_service,
    form: OAuth2PasswordRequestForm = Depends(),
):
    return await service.login_user(
        UserLogin(
            email=form.username,
            password=form.password,
        )
    )

@router.get("/profile", response_model=UserOutput)
async def get_user_profile(
    service: user_service,
    user_id: CurrentUserID,
) -> UserOutput:
    return await service.get_user_profile(user_id)


@router.put("/profile", response_model=UserOutput)
async def update_user_profile(
    service: user_service,
    user_id: CurrentUserID,
    user_update:UserUpdate = Depends(),
) -> UserOutput:
    return await service.update_user_profile(user_id, user_update)