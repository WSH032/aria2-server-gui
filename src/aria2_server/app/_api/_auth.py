"""User authentication and management API routes.

Visit <https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/>
to know how to use these routes.
"""

from typing import Any, Sequence

from fastapi_users.authentication import AuthenticationBackend

from aria2_server.app.core._auth import (
    AUTH_COOKIE_NAME,
    COOKIE_SECURE,
    fastapi_users_helper,
)
from aria2_server.db.user.schemas import UserRead, UserUpdate

__all__ = ("AUTH_COOKIE_NAME", "COOKIE_SECURE", "auth_router", "users_router")


# HACK: this is fastapi-users typing issue
_backends: Sequence[
    AuthenticationBackend[Any, Any]
] = fastapi_users_helper.authenticator.backends  # pyright: ignore[reportUnknownMemberType]
# we only design it for cookie_database backend currently
assert len(_backends) == 1, "not only one auth backend"
_auth_backend = _backends[0]


# HACK: this is fastapi-users typing issue
auth_router = fastapi_users_helper.get_auth_router(_auth_backend)  # pyright: ignore[reportUnknownMemberType]
users_router = fastapi_users_helper.get_users_router(
    user_schema=UserRead, user_update_schema=UserUpdate
)
