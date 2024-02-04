from inspect import Parameter
from pathlib import Path
from typing import Union

import nicegui
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.routing import APIRoute
from nicegui import APIRouter as GuiRouter
from nicegui import app as _app
from nicegui import ui
from nicegui.server import Server as NiceguiServer

from aria2_server._gui.components.aria_ng_iframe import AriaNgIframe
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
    make_args_required,
)
from aria2_server.config import GLOBAL_CONFIG
from aria2_server.static import favicon

__all__ = ("Server", "auth_dependency_helper_")


class _SecureStyledForm(StyledForm):
    pass


_SecureStyledForm.req_secure_context_by_default = _api.auth.COOKIE_SECURE


# auth dependency utils
auth_dependency_helper_ = AuthRedirectDependency(
    redirect_url="/account", fastapi_users=fastapi_users_helper
)
"""This is private, only for internal use."""
auth_dependency_helper_.require_superuser = False

_auth_dependency = auth_dependency_helper_.auth_redirect_dependency


class _AllowUnauthRouter(GuiRouter):
    def ignore_all_endpoints(self, auth_dependency_helper_: AuthRedirectDependency, /):
        """Call this method after all endpoints are added to this router."""
        for route in self.routes:
            assert isinstance(route, APIRoute)
            auth_dependency_helper_.ignore_exception(route.endpoint)


_gui_router = GuiRouter()
_allow_unauth_gui_router = _AllowUnauthRouter()
_api_router = APIRouter(prefix="/api", tags=["api"])


##### ui router #####


@_gui_router.page("/", dependencies=[Depends(_auth_dependency)])  # type: ignore
def index():
    with ui.card().classes("absolute-center"):
        ui.markdown("## Welcome to Aria2 Server")
        ui.button("Enter AriaNg", on_click=lambda: ui.open("/AriaNg"))
        ui.button("Account", on_click=lambda: ui.open("/account"))


@_gui_router.page("/AriaNg", dependencies=[Depends(_auth_dependency)])  # type: ignore
def aria_ng(request: Request):
    # TODO: add quasar drawer
    # see https://nicegui.io/documentation/section_pages_routing#page_layout

    # By default, NiceGUI provides a built-in padding around the content of the page,
    # We can remove it by adding the "p-0" class to the content element
    ui.query(".nicegui-content").classes("p-0")
    with ui.card().tight().classes("w-screen h-screen"):
        aria_ng_src = request.scope.get("root_path", "") + "/static/AriaNg"
        AriaNgIframe(
            aria_ng_src=aria_ng_src,
            interface="api/aria2/jsonrpc",
            secret=GLOBAL_CONFIG.aria2.rpc_secret.get_secret_value(),
        ).props("height=100%").props("width=100%").style("border: none;")


@_allow_unauth_gui_router.page("/account")  # type: ignore
def account(user: Union[User, None] = Depends(_auth_dependency)):
    if user is None:
        with ui.card().classes("absolute-center"):
            StyledLabel("Login your account to continue")
            with _SecureStyledForm() as login_form:
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
                with _SecureStyledForm() as patch_form:
                    # https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/#patch-me
                    EmailInput(name="email")
                    PasswordInput(name="password", pwd_autocomplete="new-password")
                    SubmitButton("Patch")
                    patch_form.method("PATCH").enctype("application/json").action(
                        "/api/users/me"
                    )

            with ui.card():
                StyledLabel("Logou your account")
                with _SecureStyledForm() as logout_form:
                    # https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/#post-logout
                    SubmitButton("Logout")
                    logout_form.method("POST").enctype(
                        "application/x-www-form-urlencoded"
                    ).action("/api/auth/logout")


##### api router #####


# NOTE: aria2 proxy router must be protected by user auth,
# because `AriaNgIframe` expose aria2c rpc-secret in `src` of <iframe>,
# e.g <iframe src="...secret=...">
aria2_proxy_assembly = _api.aria2.build_aria2_proxy_on(
    APIRouter(dependencies=[Depends(_auth_dependency)])
)
_app.on_shutdown(aria2_proxy_assembly.on_shutdown)  # pyright: ignore[reportUnknownMemberType]
_api_router.include_router(aria2_proxy_assembly.router, prefix="/aria2", tags=["aria2"])

_api_router.include_router(_api.auth.auth_router, prefix="/auth", tags=["auth"])
_api_router.include_router(_api.auth.users_router, prefix="/users", tags=["users"])


##### assembly #####

_app.mount("/static/AriaNg", aria_ng_app(FastAPI()), name="AriaNg-static")
_app.include_router(_api_router)
_app.include_router(_gui_router)
_app.include_router(_allow_unauth_gui_router)
# ignore auth exception for all endpoints in _allow_unauth_router
_allow_unauth_gui_router.ignore_all_endpoints(auth_dependency_helper_)


##### utils #####


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