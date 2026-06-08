from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_session
from src.models.users import User
from src.schemas.User import UserCreate, UserOutput, UserLoginOutput, UserLogin,UserUpdate 
from src.core.file_handler import save_image
from src.utils.password import hash_password, verify_password
from src.core.jwt_auth import create_access_token
from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import noload
from uuid import UUID
class UsersService:
    def __init__(self, db:AsyncSession):
        self.db = db
        
    
    async def create_user(self,user:UserCreate)->UserOutput:
        user_data =  user.model_dump()
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
        return UserOutput.model_validate(user)
    
    async def login_user(self, user:UserLogin) -> UserLoginOutput:
        plain_password = user.password
        user = (
            await self.db.execute(
                select(User)
                .options(noload(User.api_key))
                .where(User.email == user.email)
            )
        ).scalar_one_or_none()
        
        if not user or not verify_password(plain_password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return UserLoginOutput(
            access_token=create_access_token({
                "user_id": user.id,
                "email": user.email,
            })
        )


    async def get_user_profile(self, user_id: UUID) -> UserOutput:
        user = (
            await self.db.execute(
                select(User)
                .options(noload(User.api_key))
                .where(User.id == user_id)
            )
        ).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserOutput.model_validate(user)



    async def update_user_profile(self, user_id: UUID, user_update: UserUpdate) -> UserOutput:
        user = (
            await self.db.execute(
                select(User)
                .options(noload(User.api_key))
                .where(User.id == user_id)
            )
        ).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
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
    
    


def get_user_service(db:get_session)->UsersService:
    return UsersService(db)

user_service = Annotated[UsersService, Depends(get_user_service)]