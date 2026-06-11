import secrets
from decouple import config
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_session
from src.models.permission import (
    Permission,
    Role,
    RolePermission,
    UserPermission,
    UserRole,
)
from src.models.users import TokenType, User, UserToken
from src.schemas.User import (
    UserApiKey,
    UserCreate,
    UserOutput,
    UserLoginOutput,
    UserLogin,
    UserPasswordReset,
    UserUpdate,
)
from src.core.file_handler import save_image
from src.utils.password import hash_password, verify_password
from src.core.jwt_auth import create_access_token
from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload, selectinload
from uuid import UUID
from src.core.email import EmailEngine
from datetime import datetime, timedelta



class UsersService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_service = EmailEngine()
        

    
    # ======== Send Email Verification ======== #
    async def send_email_verification(self,email:str)  -> bool:
        
        
        stmt = (
             select(User).options(
                noload(User.api_key),
                joinedload(User.user_token)
            ).where(User.email == email)
        )
        
        query = await self.db.execute(stmt)
        user = query.scalar_one_or_none()
        
        await self.email_service.send_email(
            email=email,
            subject="Email Verification",
            template_name="verify_email.html",
            otp=user.user_token.token,
            username=user.name,
            expiry_minutes=int(config("VERIFICTION_EXPIRE_TIME", default=10)),
        )
        print(f"Email sent to {email}")
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        print(f"Email sent to {email}")
        return True
    
    
    # ======== Create User ======== #
    async def create_user(self, user: UserCreate) -> UserOutput:
        user_data = user.model_dump()
        data = user_data.copy()
        print(data)
        data["password"] = hash_password(data["password"])
        print(data["password"])
        user = User(
            **data,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        await self.send_email_verification(user.email)
        return UserOutput.model_validate(user)
    
    # ======== Verify Email ======== #  
    async def verify_email(self, otp: str) -> dict:
        token_stmt = (
            select(
                UserToken
            ).join(UserToken.user).options(
                joinedload(UserToken.user)
            ).where(UserToken.token == otp , UserToken.created_at <= datetime.now() - timedelta(seconds=int(config("VERIFICTION_EXPIRE_TIME"))*60))
        )
        print(token_stmt)
        token_query = await self.db.execute(token_stmt)
        print(token_query)
        token = token_query.scalar_one_or_none()
        print(token)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid OTP"
            )
        token.user.is_verified = True
        await self.db.delete(token)
        await self.db.commit()
        await self.db.refresh(token.user)
        return {"message": "Email verified successfully", "user": UserOutput.model_validate(token.user)}
    
    
    # ======== Login ======== #
    async def login_user(self, user: UserLogin) -> UserLoginOutput:
        plain_password = user.password
        user = (
            await self.db.execute(
                select(User)
                .options(noload(User.api_key))
                .where(User.email == user.email)
            )
        ).scalar_one_or_none()

        if not user or not verify_password(plain_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified"
            )
        return UserLoginOutput(
            access_token=create_access_token(
                {
                    "user_id": user.id,
                    "email": user.email,
                }
            )
        )

    # ======== Get Profile ======== #
    async def get_user_profile(self, user_id: UUID) -> UserOutput:
        user = (
            await self.db.execute(
                select(User)
                .options(
                    noload(User.api_key),
                    noload(User.user_token),
                    selectinload(User.user_roles)
                    .selectinload(UserRole.role)
                    .selectinload(Role.role_permissions)
                    .selectinload(RolePermission.permission),
                    selectinload(User.user_permissions).selectinload(
                        UserPermission.permission
                    ),
                )
                .where(User.id == user_id)
            )
        ).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserOutput.model_validate(user)

    # ======== Update Profile ======== #
    async def update_user_profile(
        self, user_id: UUID, user_update: UserUpdate
    ) -> UserOutput:
        user = (
            await self.db.execute(
                select(User).options(noload(User.api_key)).where(User.id == user_id)
            )
        ).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        update_data = user_update.model_dump().copy()
        image = update_data.pop("image")
        for key, value in update_data.items():
            setattr(user, key, value)
        if image:
            image_url = save_image(folder="users", name=user.id, file=image)
            user.image_url = image_url
        await self.db.commit()
        await self.db.refresh(user)
        return UserOutput.model_validate(user)


    # ======== Reset Password ======== #
    async def reset_password(self, user_id: UUID, password: UserPasswordReset) -> dict:
        user_stmt = (
            select(User).options(noload(User.api_key)).where(User.id == user_id)
        )
        user_query = await self.db.execute(user_stmt)
        user = user_query.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if password.password != password.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password and confirm password do not match"
            )
        user.password = hash_password(password.password)
        await self.db.commit()
        await self.db.refresh(user)
        return {"message": "Password reset successfully"}
   
   
    # ======== Generate Password Reset Token ======== #
    async def generate_password_reset_token(self) -> str:
        while True:
            otp = f"{secrets.randbelow(10000):04d}"
            exsits_token = (
                select(UserToken).where(UserToken.token == otp)
            )
            token_query = await self.db.execute(exsits_token)
            token = token_query.scalar_one_or_none()
            if not token:
                break
        return otp
   
    # ======== Send Password Reset Email ======== #
    async def send_password_reset_email(self, email: str, username: str, otp: str   ) -> dict:
        await self.email_service.send_email(
            email=email,
            subject="Your RevGAPI password reset code",
            template_name="forgot_password.html",
            username=username,
            otp=otp,
            expiry_minutes=int(config("VERIFICTION_EXPIRE_TIME", default=10)),
        )
        return {"message": "Password reset email sent"}
    
    
    
    # ======== Forgot Password ======== #
    async def forgot_password(self, email: str) -> dict:
        user_stmt = (
            select(User).options(noload(User.api_key),joinedload(User.user_token)).where(User.email == email)
        )
        user_query = await self.db.execute(user_stmt)
        user = user_query.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        otp = await self.generate_password_reset_token()    
        if not user.user_token:
            user.user_token = UserToken(
                token=otp,
                token_type=TokenType.fp,
                user_id=user.id
            )
            self.db.add(user.user_token)
        else:
            user.user_token.token = otp
            user.user_token.token_type = TokenType.fp
        await self.db.commit()
        await self.db.refresh(user)
        await self.send_password_reset_email(user.email, user.name, otp)
        return {"message": "Password reset email sent"}

    # ======== Verify Password Reset Token ======== #
    async def verify_password_reset_token(self, otp: str) -> dict:
        token_stmt = (
            select(UserToken).where(UserToken.token == otp , UserToken.created_at <= datetime.now() - timedelta(seconds=int(config("VERIFICTION_EXPIRE_TIME"))*60))
        )
        token_query = await self.db.execute(token_stmt)
        token = token_query.scalar_one_or_none()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid OTP"
            )
        if token.token_type != TokenType.fp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
            )
        return {"message": "Password reset token verified" }
    
    # ======== Reset Password with Token ======== #
    async def reset_password_with_token(self, token: str, password: UserPasswordReset) -> dict:
        stmt = (
            select(UserToken).join(UserToken.user).options(joinedload(UserToken.user)).where(UserToken.token == token , UserToken.created_at <= datetime.now() - timedelta(seconds=int(config("VERIFICTION_EXPIRE_TIME"))*60))
        )
        query = await self.db.execute(stmt)
        token = query.scalar_one_or_none()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session expired"
            )
        if token.token_type != TokenType.fp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Session expired"
            )
        user = token.user   
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if password.password != password.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password and confirm password do not match"
            )
        user.password = hash_password(password.password)
        await self.db.delete(token)
        await self.db.commit()
        await self.db.refresh(user)
        return {"message": "Password reset successfully"}

    # ======== Generate Api Key ======== #
    async def get_user_api_key(self, user_id: UUID) -> UserApiKey:
        user_stmt = (
            select(User).join(User.api_key).options(joinedload(User.api_key)).where(User.id == user_id)
        )
        user_query = await self.db.execute(user_stmt)
        user = user_query.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserApiKey.model_validate(user.api_key)





def get_user_service(db: get_session) -> UsersService:
    return UsersService(db)


user_service = Annotated[UsersService, Depends(get_user_service)]
