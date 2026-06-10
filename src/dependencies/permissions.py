from  fastapi import Depends, HTTPException, status
from  sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_session
from .get_user import CurrentUserID
from src.core.permissions import PermissionEngine
from typing import Literal

def required_permissions(
    permissions:list[str],
    mode:Literal["ANY","ALL"] = "ANY",
):
    
    
    async def checker(
        user_id:CurrentUserID,
        session:get_session
    ):
        engine = PermissionEngine(session)
        
        allowed = await engine.has_permission(
            user_id,
            permissions,
            mode,
        )
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this resource")
        return user_id
    return checker