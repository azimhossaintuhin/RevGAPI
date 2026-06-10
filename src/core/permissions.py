from  sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.permission import Permission , UserPermission , UserRole, RolePermission
from uuid import UUID
from typing import Literal

class PermissionEngine:
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    
    async def get_user_permissions(self, user_id:UUID) -> set[str]:
        
        result =  await self.session.execute(
            select(Permission.code).
            join(RolePermission,RolePermission.permission_id == Permission.id).
            join(UserRole,UserRole.role_id == RolePermission.role_id).
            where(UserRole.user_id == user_id)
        )
        
        reole_permission = {row[0] for row in result.all()}
      

        user_result =  await self.session.execute(
            select(Permission.code).
            join(UserPermission,UserPermission.permission_id == Permission.id).
            where(UserPermission.user_id == user_id)
        )
        
        user_permission = {row[0] for row in user_result.all()}
        
        return reole_permission | user_permission
    
    
    async def  has_permission(self, user_id:UUID, permissions:list[str], mode:Literal["ANY","ALL"] = "ANY") -> bool:
        user_perms = await self.get_user_permissions(user_id)
        requierd = set(permissions)
        
        if mode == "ANY":
            return len(user_perms.intersection(requierd)) > 0
        if mode == "ALL":
            return requierd.issubset(user_perms)
        
        return False