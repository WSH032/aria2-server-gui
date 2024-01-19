from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy import UUID_ID
from sqlalchemy.ext.asyncio import AsyncSession

from aria2_server.db._core import (
    get_async_session,
)
from aria2_server.db.user.models import (
    User,
)

__all__ = ("SQLAlchemyUserDatabase", "get_user_db")


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[User, UUID_ID], None]:
    yield SQLAlchemyUserDatabase[User, UUID_ID](session, User)
