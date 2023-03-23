from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import  AsyncSession,async_sessionmaker
from sqlalchemy.ext.asyncio.scoping import async_scoped_session
from asyncio import current_task
from sqlalchemy.orm import sessionmaker
import asyncio
from typing import AsyncGenerator, Callable, Type
from fastapi import Depends
from settings import AppSettings,get_app_settings
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import datetime

class ModelMixin(object):

    created = sa.Column(
        sa.DateTime,
        default=datetime.datetime.now,
        nullable=False
    )
    last_update = sa.Column(
        sa.DateTime,
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


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session



def get_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[AsyncSession], BaseRepository]:
    def _get_repo(
        conn: AsyncSession = Depends(get_session),
    ) -> BaseRepository:
        return repo_type(conn)

    return _get_repo




engine = create_async_engine(
    str(get_app_settings().ASYNC_PG_DSN)
)

async_session = async_scoped_session(
    sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False #@https://github.com/sqlalchemy/sqlalchemy/discussions/6165
    ),
    scopefunc=current_task,
)

# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(DeclarativeBase.metadata.create_all)

# asyncio.run(init_models())