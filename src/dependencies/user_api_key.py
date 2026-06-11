from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db
from src.models.users import User, ApiKey
from sqlalchemy import select
from typing import Annotated, Tuple


async def get_user_api_key(
    api_key:str = Header(...,alias="X-API-Key"),
    db:AsyncSession = Depends(get_db)
) -> User:
    result = await db.execute(
         select(ApiKey).where(
             ApiKey.api_key == api_key
         )
    )
    key_obj = result.scalar_one_or_none()
    
    if not key_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    
    if key_obj.is_deleted or not key_obj.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key is deleted")
    
    if not key_obj.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key is not active")
    
    user = await db.execute(
        select(User).where(
            User.id == key_obj.user_id
        )
    )
    user_obj = user.scalar_one_or_none()
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user_obj 


UserApiKey = Annotated[User, Depends(get_user_api_key)]