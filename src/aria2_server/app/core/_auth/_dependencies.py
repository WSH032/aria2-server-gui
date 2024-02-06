from typing import (
    Any,
    Mapping,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from fastapi import Depends, HTTPException, WebSocketException
from fastapi.requests import HTTPConnection
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import (
    DatabaseStrategy,
)
from fastapi_users_db_sqlalchemy import UUID_ID
from typing_extensions import Annotated

from aria2_server.app.core._auth._api_key import ConnAPIKeyCookie
from aria2_server.app.core._auth._core import UserManager, fastapi_users_helper
from aria2_server.db.access_token import AccessToken
from aria2_server.db.user import User

__all__ = ("UserRedirect",)


_UserTypeVar = TypeVar("_UserTypeVar", bound=User)


# HACK: this is fastapi-users typing issue
_authenticator_backends: Sequence[
    AuthenticationBackend[User, UUID_ID]
] = fastapi_users_helper.authenticator.backends  # pyright: ignore[reportUnknownMemberType]

# we only design it for cookie_database backend currently
assert len(_authenticator_backends) == 1, "More than one cookie_database backend"
assert isinstance(_authenticator_backends[0], AuthenticationBackend)
assert (
    _authenticator_backends[0].name == "cookie_database"
), "Is not cookie_database backend"
_cookie_database_backend = _authenticator_backends[0]

# for typing hint
assert isinstance(_cookie_database_backend.transport, CookieTransport)
_cookie_database_backend_transport = _cookie_database_backend.transport
_cookie_database_backend_get_strategy = _cookie_database_backend.get_strategy


class UserRedirect:
    """This dependency can be used for both HTTP and WebSocket.

    While optional is False, if can not get a user, or the user is not valid, will raise an exception to redirect.
    You can use `self.check_user` to check the user is valid or not.
    """

    def __init__(
        self,
        redirect_url: str,
        *,
        use_root_path: bool,
        # http exception
        status_code: int,
        detail: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        # websocket exception
        code: int,
        reason: Optional[str] = None,
        # fastapi-users
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
    ):
        self.redirect_url = redirect_url
        self.use_root_path = use_root_path
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        self.code = code
        self.reason = reason
        self.optional = optional
        self.active = active
        self.verified = verified
        self.superuser = superuser

    # TODO, FIXME, HACK: Can not use `fastapi_user.current_user()` directly,
    # See: https://github.com/fastapi-users/fastapi-users/issues/295
    #      https://github.com/fastapi-users/fastapi-users/discussions/436
    #      https://github.com/tiangolo/fastapi/discussions/8983
    async def __call__(
        self,
        conn: HTTPConnection,
        user_manager: Annotated[
            UserManager, Depends(fastapi_users_helper.get_user_manager)
        ],
        token: Annotated[
            Union[str, None],
            Depends(
                ConnAPIKeyCookie(
                    name=_cookie_database_backend_transport.cookie_name,
                    auto_error=False,
                )
            ),
        ],
        strategy: Annotated[
            DatabaseStrategy[User, UUID_ID, AccessToken],
            Depends(_cookie_database_backend_get_strategy),
        ],
    ) -> Optional[User]:
        # Modified: https://github.com/fastapi-users/fastapi-users/blob/ae9f52474ba2c7baebeb923e4d03aea479765362/fastapi_users/authentication/authenticator.py#L148-L186

        if token is not None:
            user = await strategy.read_token(token, user_manager)
        else:
            user = None

        if not self.optional and (user is None or self.check_user(user) is None):
            if self.use_root_path:
                _redirect_url = conn.scope.get("root_path", "") + self.redirect_url
            else:
                _redirect_url = self.redirect_url

            msg = f"Unauthorized, Please redirect to {_redirect_url} to login."
            scope_type = conn.scope.get("type")

            if scope_type == "websocket":
                # TODO: support WebSocket Denial Response
                # see https://github.com/encode/starlette/releases/tag/0.37.0
                reason = self.reason if self.reason is not None else msg
                raise WebSocketException(
                    code=self.code,
                    reason=reason,
                )
            elif scope_type == "http":
                detail = self.detail if self.detail is not None else msg
                headers = {"Location": _redirect_url, **(self.headers or {})}
                raise HTTPException(
                    status_code=self.status_code,
                    detail=detail,
                    headers=headers,
                )
            else:
                raise AssertionError("Unknown scope type")

        return user

    def check_user(
        self,
        user: _UserTypeVar,
    ) -> Optional[_UserTypeVar]:
        """If the user is not valid, return None. Otherwise, return the user.

        If the user is not valid, `self.__call__` should raise an exception.
        """
        if (
            (self.active and not user.is_active)
            or (self.verified and not user.is_verified)
            or (self.superuser and not user.is_superuser)
        ):
            return None
        return user
