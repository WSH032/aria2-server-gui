import functools
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from typing_extensions import assert_never

from aria2_server.config import get_current_config

__all__ = (
    "AsyncEngine",
    "AsyncSession",
    "async_sessionmaker",
    "get_async_session",
    "get_current_db_url",
    "get_global_async_session_maker",
    "get_global_engine",
)


# 1 for singleton pattern
_CACHE_MAXSIZE = 1


def get_current_db_url() -> str:
    """This function returns the db url according to the current global config."""
    sqlite_url_prefix = "sqlite+aiosqlite:///"
    sqlite_db_path = get_current_config().server.extra.sqlite_db

    if isinstance(sqlite_db_path, Path):
        sqlite_db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite_url_prefix + sqlite_db_path.as_posix()
    elif sqlite_db_path == ":memory:":
        return sqlite_url_prefix + sqlite_db_path
    else:
        assert_never(sqlite_db_path)


@functools.lru_cache(maxsize=_CACHE_MAXSIZE)
# NOTE: use `/` to keep the same parameter pattern,
# see: https://docs.python.org/3/library/functools.html#functools.lru_cache
def _get_engine_from_url(url: str, /) -> AsyncEngine:
    return create_async_engine(url, connect_args={"check_same_thread": False})


def get_global_engine() -> AsyncEngine:
    """Return the global engine.

    This is a lru_cache function, which returns the same object every time you call it,
    as long as you don't change global config.
    """
    db_url = get_current_db_url()
    return _get_engine_from_url(db_url)


@functools.lru_cache(maxsize=_CACHE_MAXSIZE)
# NOTE: use `/` to keep the same parameter pattern,
# see: https://docs.python.org/3/library/functools.html#functools.lru_cache
def _get_async_session_maker_from_engine(
    engine: AsyncEngine, /
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


def get_global_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """Return the global async_session_maker.

    This is a lru_cache function, which returns the same object every time you call it,
    as long as you don't change global config.
    """
    global_engine = get_global_engine()
    return _get_async_session_maker_from_engine(global_engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Every time you call this function, it returns a new session."""
    global_async_session_maker = get_global_async_session_maker()
    async with global_async_session_maker() as session:
        yield session
