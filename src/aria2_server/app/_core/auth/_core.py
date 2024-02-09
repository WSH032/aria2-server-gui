from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy import UUID_ID

from aria2_server.config import GLOBAL_CONFIG
from aria2_server.db.access_token import AccessToken, get_access_token_db
from aria2_server.db.user import User, get_user_db

__all__ = (
    "AUTH_COOKIE_NAME",
    "COOKIE_SECURE",
    "UUID_ID",
    "User",
    "UserManager",
    "fastapi_users_helper",
    "get_user_manager",
)


AUTH_COOKIE_NAME = "fastapiusersauth"

COOKIE_SECURE = True


# NOTE: Don't unpack `GLOBAL_CONFIG` outside of a function
_cookie_transport = CookieTransport(
    AUTH_COOKIE_NAME,
    cookie_max_age=GLOBAL_CONFIG.server.extra.expiration_second,
    cookie_secure=COOKIE_SECURE,
)


def _get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy[User, UUID_ID, AccessToken]:
    # NOTE: Don't unpack `GLOBAL_CONFIG` outside of a function
    return DatabaseStrategy[User, UUID_ID, AccessToken](
        access_token_db, lifetime_seconds=GLOBAL_CONFIG.server.extra.expiration_second
    )


_auth_backend = AuthenticationBackend(
    name="cookie_database",
    transport=_cookie_transport,
    get_strategy=_get_database_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID_ID]):
    pass


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[User, UUID_ID] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


fastapi_users_helper = FastAPIUsers[User, UUID_ID](
    get_user_manager,
    [_auth_backend],
)
