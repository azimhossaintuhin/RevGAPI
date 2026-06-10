from __future__ import annotations

from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid

from src.config.database import Base
from .users import User








class PermissionModule(Base):
    __tablename__ = "permission_modules"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:Mapped[str] = mapped_column(String(255), nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    permissions:Mapped[list["Permission"]] = relationship("Permission", back_populates="module" , cascade="all, delete-orphan")


class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("permission_modules.id" , ondelete="CASCADE"), nullable=False)
    name:Mapped[str] = mapped_column(String(255), nullable=False)
    code:Mapped[str] = mapped_column(String(255), nullable=False)
    description:Mapped[str] = mapped_column(String(255), nullable=False)
    module:Mapped[PermissionModule] = relationship("PermissionModule", back_populates="permissions")
    role_permissions:Mapped[list["RolePermission"]] = relationship("RolePermission", back_populates="permission")
    user_permissions:Mapped[list["UserPermission"]] = relationship("UserPermission", back_populates="permission")
    created_at:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
         


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:Mapped[str] = mapped_column(String(255), nullable=False)
    role_permissions:Mapped[list["RolePermission"]] = relationship("RolePermission", back_populates="role")
    user_roles:Mapped[list["UserRole"]] = relationship("UserRole", back_populates="role")
    created_at:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

class RolePermission(Base):
    __tablename__ = "role_permissions"
    id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id" , ondelete="CASCADE"), nullable=False)
    permission_id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("permissions.id" , ondelete="CASCADE"), nullable=False)
    role:Mapped[Role] = relationship("Role", back_populates="role_permissions")
    permission:Mapped[Permission] = relationship("Permission", back_populates="role_permissions" )
    created_at:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    

class UserRole(Base):
    __tablename__ = "user_roles"
    id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id" , ondelete="CASCADE"), nullable=False)
    role_id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id" , ondelete="CASCADE"), nullable=False)
    user:Mapped[User] = relationship("User", back_populates="user_roles" )
    role:Mapped[Role] = relationship("Role", back_populates="user_roles")
    created_at:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())


class UserPermission(Base):
    __tablename__ = "user_permissions"
    id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id" , ondelete="CASCADE"), nullable=False)
    permission_id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("permissions.id" , ondelete="CASCADE"), nullable=False)
    user:Mapped[User] = relationship("User", back_populates="user_permissions")
    permission:Mapped["Permission"] = relationship("Permission", back_populates="user_permissions" )
    created_at:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    
