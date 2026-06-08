from sqlalchemy.ext.asyncio  import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from decouple import config
from  typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = f"postgresql+asyncpg://{config('POSTGRES_USER')}:{config('POSTGRES_PASSWORD')}@{config('POSTGRES_HOST')}:{config('POSTGRES_PORT')}/{config('POSTGRES_DB')}"

async_engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker[AsyncSession](async_engine, class_=AsyncSession, expire_on_commit=False )


async  def get_db()->AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


get_session = Annotated[AsyncSession, Depends(get_db)]


class Base(DeclarativeBase):
    pass