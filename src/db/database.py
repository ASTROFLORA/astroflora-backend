from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator


DATABASE_URL = "postgresql+asyncpg://luiso:123@localhost:5432/astroflora_db"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


Base = declarative_base()

async def get_async_session():
    async with async_session() as session:
        yield session