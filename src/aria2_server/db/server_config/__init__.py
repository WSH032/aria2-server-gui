from typing import Any, AsyncGenerator, Dict, Type

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aria2_server.db._core import (
    get_async_session,
)
from aria2_server.db.server_config.models import ServerConfig

__all__ = ("ServerConfigDatabase", "get_server_config_db")


class ServerConfigDatabase:
    def __init__(self, session: AsyncSession, server_config_table: Type[ServerConfig]):
        self.session = session
        self.server_config_table = server_config_table

    async def _create(self) -> ServerConfig:
        server_config = self.server_config_table()
        self.session.add(server_config)
        await self.session.commit()
        await self.session.refresh(server_config)
        return server_config

    async def get(self) -> ServerConfig:
        results = await self.session.execute(select(self.server_config_table))
        server_config = results.scalar_one_or_none()  # only allow one row
        if server_config is None:
            return await self._create()
        return server_config

    async def update(self, update_dict: Dict[str, Any]) -> ServerConfig:
        server_config = await self.get()
        for key, value in update_dict.items():
            setattr(server_config, key, value)
        await self.session.commit()
        await self.session.refresh(server_config)
        return server_config


async def get_server_config_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[ServerConfigDatabase, None]:
    yield ServerConfigDatabase(session, ServerConfig)
