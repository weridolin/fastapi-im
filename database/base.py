from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import  AsyncSession,async_sessionmaker
from sqlalchemy.ext.asyncio.scoping import async_scoped_session
from asyncio import current_task
from sqlalchemy.orm import sessionmaker
import asyncio
from typing import AsyncGenerator, Callable, Type


import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import datetime

class ModelMixin(object):

    created = sa.Column(
        sa.DateTime(timezone=True),
        default=datetime.datetime.now,
        nullable=False
    )
    last_update = sa.Column(
        sa.DateTime(timezone=True),
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False
    )

DeclarativeBase = declarative_base(cls=ModelMixin)


class BaseRepository:
    def __init__(self, conn: AsyncSession) -> None:
        self._conn = conn

    @property
    def connection(self) -> AsyncSession:
        return self._conn



DB_URL = "sqlite+aiosqlite:///im.db" ## TODO


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

# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(DeclarativeBase.metadata.create_all)


# # Dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# asyncio.run(init_models())