from src.config.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy import func
import uuid
import secrets
from src.core.file_handler import save_image


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    api_key: Mapped["ApiKey"] = relationship("ApiKey", back_populates="user" , lazy="joined" ,uselist=False)
    def __repr__(self):
        return f"<User {self.name}>" 

class ApiKey(Base):
    __tablename__ = "api_keys"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id",ondelete="CASCADE"), nullable=False , unique=True)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False, default=lambda:f"ari-api-{secrets.token_hex(32)}")
    api_secret: Mapped[str] = mapped_column(String(255), nullable=False, default=lambda:f"ari-api-secret-{secrets.token_hex(32)}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    per_day_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    remaining_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    user: Mapped[User] = relationship("User", back_populates="api_key" ,uselist=False)
    def __repr__(self):
        return f"<ApiKey {self.id}>" 
    
