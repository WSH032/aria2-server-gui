from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from typing_extensions import assert_never

from aria2_server.config import GLOBAL_CONFIG

__all__ = (
    "DATABASE_URL",
    "engine",
    "async_session_maker",
    "get_async_session",
    "AsyncSession",
)


_sqlite_url_prefix = "sqlite+aiosqlite:///"


# TODO: Don't unpack `GLOBAL_CONFIG` outside of a function
_sqlite_db_path = GLOBAL_CONFIG.server.sqlite_db

if isinstance(_sqlite_db_path, Path):
    _sqlite_db_path.parent.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = _sqlite_url_prefix + _sqlite_db_path.as_posix()
elif _sqlite_db_path == ":memory:":
    DATABASE_URL = _sqlite_url_prefix + _sqlite_db_path  # pyright: ignore[reportConstantRedefinition]
else:
    assert_never(_sqlite_db_path)


engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
