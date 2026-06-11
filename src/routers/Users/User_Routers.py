from fastapi.security import OAuth2PasswordRequestForm
from uuid import UUID
from src.dependencies.get_user import CurrentUserID
from src.schemas.User import UserApiKey, UserCreate, UserForgotPassword, UserOutput, UserLoginOutput, UserLogin, UserPasswordReset, UserUpdate, UserVerifyPasswordResetToken
from src.services.users.Users import user_service
from fastapi import APIRouter, Depends, HTTPException, Query
from src.dependencies.permissions import required_permissions




router = APIRouter(prefix="/users", tags=["users"])


# ======== Create User ======== #
@router.post("/create", response_model=UserOutput)
async def create_user(user: UserCreate, service: user_service) -> UserOutput:
    return await service.create_user(user)


# ======== Verify Email ======== #
@router.post("/verify-email", response_model=dict)
async def verify_email(
    service: user_service,
    otp: str,
) -> dict:
    return await service.verify_email(otp)

# ======== Login ======== #
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

# ======== Get Profile ======== #
@router.get("/profile", response_model=UserOutput)
async def get_user_profile(
    service: user_service,
    user_id: CurrentUserID
) -> UserOutput:
    return await service.get_user_profile(user_id)


# ======== Update Profile ======== #
@router.put("/profile", response_model=UserOutput)
async def update_user_profile(
    service: user_service,
    user_id: CurrentUserID,
    user_update: UserUpdate = Depends(),
    
) -> UserOutput:
    return await service.update_user_profile(user_id, user_update)


# ======== Change Password ======== #
@router.post("/change-password", response_model=dict)
async def change_password(
    service: user_service,
    user_id: CurrentUserID,
    password: UserPasswordReset,
) -> dict:
    return await service.reset_password(user_id, password)



# ======== Forget Password ======== #
@router.post("/forget-password", response_model=dict)
async def forgot_password(
    service: user_service,
    user: UserForgotPassword,
) -> dict:
    return await service.forgot_password(user.email)

# ======== Verify Password Reset Token ======== #
@router.post("/verify-password-reset-token", response_model=dict)
async def verify_password_reset_token(
    service: user_service,
    otp: UserVerifyPasswordResetToken,
) -> dict:
    return await service.verify_password_reset_token(otp.otp)

# ======== Reset Password with Token ======== #

@router.post("/reset-password-with-token", response_model=dict)
async def reset_password_with_token(
    service: user_service,
    password: UserPasswordReset,
    token: str = Query(..., description="The token to reset the password")

) -> dict:
    return await service.reset_password_with_token(token, password)



# ======== Get Api Key ======== #
@router.get("/api-key", response_model=UserApiKey)
async def get_api_key(
    service: user_service,
    user_id: CurrentUserID,
) -> UserApiKey:
    return await service.get_user_api_key(user_id)  