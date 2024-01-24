import weakref
from typing import (
    Callable,
    Coroutine,
    Final,
    Sequence,
    Union,
)

from fastapi import Cookie, Depends
from fastapi.requests import HTTPConnection
from fastapi.responses import RedirectResponse
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import (
    DatabaseStrategy,
)
from fastapi_users_db_sqlalchemy import UUID_ID
from starlette import datastructures
from starlette import status as starlette_status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.exceptions import WebSocketException as StarletteWebSocketException
from typing_extensions import Annotated

from aria2_server.app.core._auth._core import UserManager
from aria2_server.db.access_token import AccessToken
from aria2_server.db.user import User
from aria2_server.types._types import AnyCallable, DecoratedCallable

__all__ = ("AuthRedirectDependency",)


class AuthRedirectDependency:
    require_verified: bool = True
    require_active: bool = True
    require_superuser: bool = True

    def __init__(
        self,
        redirect_url: str,
        fastapi_users: FastAPIUsers[User, UUID_ID],
    ):
        self.redirect_url = datastructures.URL(redirect_url)
        self.fastapi_users = fastapi_users
        self._auth_redirect_dependency = (
            None  # assigned later in `auth_redirect_dependency`
        )
        self._ignored_endpoints = weakref.WeakSet[AnyCallable]()

        # as cache, forbidden to change
        self._CACHED_HTTP_EXCEPTION: Final = self._http_exception_redirect_factory(
            self.redirect_url
        )
        self._CACHED_WS_EXCEPTION: Final = self._ws_exception_redirect_factory(
            self.redirect_url
        )

        # HACK: this is fastapi-users typing issue
        authenticator_backends: Sequence[AuthenticationBackend[User, UUID_ID]] = (
            self.fastapi_users.authenticator.backends
        )  # pyright: ignore[reportUnknownMemberType]

        # we only design it for cookie_database backend currently
        assert (
            len(authenticator_backends) == 1
            and authenticator_backends[0].name == "cookie_database"
        ), "not only one cookie_database backend"
        cookie_database_backend = authenticator_backends[0]

        # for typing hint
        assert isinstance(cookie_database_backend.transport, CookieTransport)
        self._cookie_database_backend_transport = cookie_database_backend.transport

        self._cookie_database_backend_get_strategy = (
            cookie_database_backend.get_strategy
        )

    @property
    def auth_redirect_dependency(
        self,
    ) -> Callable[
        [
            HTTPConnection,
            UserManager,
            Union[str, None],
            DatabaseStrategy[User, UUID_ID, AccessToken],
        ],
        Coroutine[None, None, Union[User, None]],
    ]:
        if self._auth_redirect_dependency is not None:
            return self._auth_redirect_dependency

        async def auth_redirect_dependency(
            conn: HTTPConnection,
            user_manager: UserManager = Depends(self.fastapi_users.get_user_manager),
            token: Annotated[
                Union[str, None],
                Cookie(alias=self._cookie_database_backend_transport.cookie_name),
            ] = None,
            strategy: DatabaseStrategy[User, UUID_ID, AccessToken] = Depends(
                self._cookie_database_backend_get_strategy
            ),
        ) -> Union[User, None]:
            if token is not None:
                user = await strategy.read_token(token, user_manager)
            else:
                user = None

            need_ignoring_exception = (
                conn.scope.get("endpoint") in self._ignored_endpoints
            )
            is_illegal = (
                not user
                or (self.require_superuser and not user.is_superuser)
                or (self.require_verified and not user.is_verified)
                or (self.require_active and not user.is_active)
            )

            if not need_ignoring_exception and is_illegal:
                if conn.scope["type"] == "http":
                    raise self._CACHED_HTTP_EXCEPTION
                elif conn.scope["type"] == "websocket":
                    raise self._CACHED_WS_EXCEPTION
                else:
                    raise AssertionError()

            return user

        self._auth_redirect_dependency = auth_redirect_dependency

        return self._auth_redirect_dependency

    @classmethod
    def _http_exception_redirect_factory(
        cls, redirect_url: datastructures.URL
    ) -> StarletteHTTPException:
        _redirect_resp_template = RedirectResponse(
            redirect_url, status_code=starlette_status.HTTP_303_SEE_OTHER
        )

        # NOTE: Do not use `headers=dict(_redirect_resp_template.header)`.
        # _redirect_resp_template.header["Content-Length"] == 0,
        # but `StarletteHTTPException` will auto set default content.
        #     https://github.com/encode/starlette/blob/363e4fb1940f0eb6e290755fddd7ea6666ce18ae/starlette/exceptions.py#L14-L15
        return StarletteHTTPException(
            status_code=_redirect_resp_template.status_code,
            headers={"location": _redirect_resp_template.headers["location"]},
            detail=f"Redirecting to {redirect_url}, please login first.",
        )

    @classmethod
    def _ws_exception_redirect_factory(
        cls, redirect_url: datastructures.URL
    ) -> StarletteWebSocketException:
        return StarletteWebSocketException(
            starlette_status.WS_1008_POLICY_VIOLATION,
            reason=f"Redirecting to {redirect_url}, please login first.",
        )

    def ignore_exception(self, endpoint: DecoratedCallable, /) -> DecoratedCallable:
        self._ignored_endpoints.add(endpoint)
        return endpoint
