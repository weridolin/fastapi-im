from sqlalchemy.ext.asyncio import create_async_engine
from models import DeclarativeBase
from sqlalchemy.ext.asyncio import  AsyncSession,async_sessionmaker
from sqlalchemy.ext.asyncio.scoping import async_scoped_session
from asyncio import current_task
from sqlalchemy.orm import sessionmaker
import asyncio

DB_URL = "sqlite+aiosqlite:///im.db"


engine = create_async_engine(
    DB_URL, 
    connect_args={"check_same_thread": False}
)
async_session = async_scoped_session(
    sessionmaker(
        engine,
        class_=AsyncSession,
    ),
    scopefunc=current_task,
)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(DeclarativeBase.metadata.create_all)


# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

asyncio.run(init_models())