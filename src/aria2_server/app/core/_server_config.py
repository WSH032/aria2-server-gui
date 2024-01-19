from contextlib import asynccontextmanager

from aria2_server.db import get_async_session
from aria2_server.db.server_config import get_server_config_db
from aria2_server.db.server_config.models import ServerConfig

__all__ = ("ServerConfig", "get_server_config_from_db")


async def get_server_config_from_db() -> ServerConfig:
    get_async_session_context = asynccontextmanager(get_async_session)
    get_server_config_db_context = asynccontextmanager(get_server_config_db)

    async with get_async_session_context() as session, get_server_config_db_context(
        session
    ) as server_config_db:
        return await server_config_db.get()
