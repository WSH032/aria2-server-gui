from inspect import Parameter
from pathlib import Path
from typing import Union

import nicegui
from fastapi import APIRouter, Depends, FastAPI
from nicegui import app as _app
from nicegui import ui
from nicegui.server import Server as NiceguiServer

from aria2_server._gui.components.q_form import (
    EmailInput,
    PasswordInput,
    StyledForm,
    StyledLabel,
    SubmitButton,
)
from aria2_server.app import _api
from aria2_server.app._subapp import aria_ng_app
from aria2_server.app.core._auth import (
    AuthRedirectDependency,
    User,
    fastapi_users_helper,
)
from aria2_server.app.core._server_config import get_server_config_from_db
from aria2_server.app.core._tools import (
    NamepaceMixin,
    get_page_routes,
    make_args_required,
)
from aria2_server.static import favicon
from aria2_server.types._types import DecoratedCallable

__all__ = ("Server", "auth_dependency_helper_")


# auth dependency utils
auth_dependency_helper_ = AuthRedirectDependency(
    redirect_url="/account", fastapi_users=fastapi_users_helper
)
"""This is private, only for internal use."""
auth_dependency_helper_.require_superuser = False

_auth_dependency = auth_dependency_helper_.auth_redirect_dependency
_ignore_auth_exception = auth_dependency_helper_.ignore_exception


def _ignore_auth_exception_on_ui_page(
    original_endpoint: DecoratedCallable,
) -> DecoratedCallable:
    """Can only be used on `@ui.page`.

    Dont use it on `@nicegui.APIrouter.page`
    """
    page_routes = get_page_routes(original_endpoint)
    assert len(page_routes) == 1, "page route not found, or found multiple routes"
    page_route = page_routes[0]
    _ignore_auth_exception(page_route.endpoint)
    return original_endpoint


# ui router
@ui.page("/", dependencies=[Depends(_auth_dependency)])
def index():
    with ui.card().classes("absolute-center"):
        ui.markdown("## Welcome to Aria2 Server")
        ui.button("Enter AriaNg", on_click=lambda: ui.open("/AriaNg"))
        ui.button("Account", on_click=lambda: ui.open("/account"))


@_ignore_auth_exception_on_ui_page
@ui.page("/account")
def account(user: Union[User, None] = Depends(_auth_dependency)):
    if user is None:
        with ui.card().classes("absolute-center"):
            StyledLabel("Login your account to continue")
            with StyledForm() as login_form:
                # https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/#post-login
                EmailInput(name="username")
                PasswordInput(name="password", pwd_autocomplete="current-password")
                SubmitButton("Login")
                login_form.method("POST").enctype(
                    "application/x-www-form-urlencoded"
                ).action("/api/auth/login").redirect_url("/")
    else:
        with ui.card().classes("absolute-center"):
            with ui.card():
                StyledLabel("Edit your account")
                with StyledForm() as patch_form:
                    # https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/#patch-me
                    EmailInput(name="email")
                    PasswordInput(name="password", pwd_autocomplete="new-password")
                    SubmitButton("Patch")
                    patch_form.method("PATCH").enctype("application/json").action(
                        "/api/users/me"
                    )

            with ui.card():
                StyledLabel("Logou your account")
                with StyledForm() as logout_form:
                    # https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/#post-logout
                    SubmitButton("Logout")
                    logout_form.method("POST").enctype(
                        "application/x-www-form-urlencoded"
                    ).action("/api/auth/logout")


_app.mount(
    "/AriaNg",
    aria_ng_app(FastAPI(dependencies=[Depends(_auth_dependency)])),
    name="AriaNg",
)

# api router
_api_router = APIRouter(prefix="/api")
_api_router.include_router(_api.auth.auth_router, prefix="/auth", tags=["auth"])
_api_router.include_router(_api.auth.users_router, prefix="/users", tags=["users"])
_app.include_router(_api_router)


class _ServerUtils(NamepaceMixin):
    get_server_config_from_db = staticmethod(get_server_config_from_db)
    favicon: Path = favicon


class Server(NamepaceMixin):
    app: nicegui.App = _app
    run = staticmethod(
        make_args_required(ui.run, (("storage_secret", Parameter.KEYWORD_ONLY),))
    )
    mount_to = staticmethod(
        make_args_required(ui.run_with, (("storage_secret", Parameter.KEYWORD_ONLY),))
    )

    @staticmethod
    def get_server() -> NiceguiServer:
        """Accessible only after startup."""
        try:
            return NiceguiServer.instance
        except AttributeError:
            raise RuntimeError("Accessible only after startup.") from None

    utils = _ServerUtils


if __name__ == "__main__":
    from aria2_server.app.main import main

    main()
