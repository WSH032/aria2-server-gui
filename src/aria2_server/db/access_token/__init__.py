from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
)
from sqlalchemy.ext.asyncio import AsyncSession

from aria2_server.db._core import get_async_session
from aria2_server.db.access_token.models import AccessToken

__all__ = ("SQLAlchemyAccessTokenDatabase", "get_access_token_db")


async def get_access_token_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyAccessTokenDatabase[AccessToken], None]:
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
