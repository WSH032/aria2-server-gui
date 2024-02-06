# HACK,TODO: This is nicegui typing hint issue
# pyright: reportUntypedFunctionDecorator=false, reportUnknownMemberType=false

from inspect import Parameter
from pathlib import Path
from textwrap import dedent
from typing import Optional, TypedDict

import nicegui
from fastapi import APIRouter, Depends, FastAPI, Request, status
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
    User,
    UserRedirect,
)
from aria2_server.app.core._server_config import get_server_config_from_db
from aria2_server.app.core._tools import (
    NamepaceMixin,
    make_args_required,
)
from aria2_server.config import GLOBAL_CONFIG
from aria2_server.static import favicon

__all__ = ("Server",)


class _SecureStyledForm(StyledForm):
    pass


_SecureStyledForm.req_secure_context_by_default = _api.auth.COOKIE_SECURE


# auth dependency utils

_REQUIRE_ACTIVE = True
_REQUIRE_VERIFIED = True
_REQUIRE_SUPERUSER = False


class _UserRedirectKwarg(TypedDict):
    redirect_url: str
    use_root_path: bool
    status_code: int
    code: int
    active: bool
    verified: bool
    superuser: bool


_user_redirect_kwargs = _UserRedirectKwarg(
    redirect_url="/account",
    use_root_path=True,
    status_code=status.HTTP_303_SEE_OTHER,
    code=status.WS_1008_POLICY_VIOLATION,
    active=_REQUIRE_ACTIVE,
    verified=_REQUIRE_VERIFIED,
    superuser=_REQUIRE_SUPERUSER,
)

_user_redirect = UserRedirect(optional=False, **_user_redirect_kwargs)
"""Will automatically raise an exception to redirect."""
_opt_user_redirect = UserRedirect(optional=True, **_user_redirect_kwargs)
"""Will not raise an exception to redirect, instead, return None."""


##### ui router #####

_gui_router = GuiRouter()


@_gui_router.page("/", dependencies=[Depends(_user_redirect)])
def index():
    with ui.card().classes("absolute-center"):
        ui.markdown("## Welcome to Aria2 Server")
        ui.button("Enter AriaNg", on_click=lambda: ui.open("/AriaNg"))
        ui.button("Account", on_click=lambda: ui.open("/account"))


@_gui_router.page("/AriaNg", dependencies=[Depends(_user_redirect)])
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


@_gui_router.page("/account")
def account(user: Optional[User] = Depends(_opt_user_redirect)):
    # before login
    if user is None:
        # login form
        with ui.card().classes("absolute-center"):
            if user is None:
                StyledLabel("Login your account to continue")
            else:
                StyledLabel("Invalid user, please login again.")
            with _SecureStyledForm() as login_form:
                # https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/#post-login
                EmailInput(name="username")
                PasswordInput(name="password", pwd_autocomplete="current-password")
                SubmitButton("Login")
                login_form.method("POST").enctype(
                    "application/x-www-form-urlencoded"
                ).action("/api/auth/login").redirect_url("/")
    # after login
    else:
        with ui.card().classes("absolute-center"):
            # check whether user is valid
            if _opt_user_redirect.check_user(user) is None:
                _msg = dedent(
                    """\
                    Warning! This is a ivnalid account.
                    Please logout and login again."""
                )
                _color = "red-600"
                StyledLabel(_msg).tailwind.text_decoration_color(
                    _color
                ).text_decoration("underline").text_color(_color)

            # edit form
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
            # logout form
            with ui.card():
                StyledLabel("Logou your account")
                with _SecureStyledForm() as logout_form:
                    # https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/#post-logout
                    SubmitButton("Logout")
                    logout_form.method("POST").enctype(
                        "application/x-www-form-urlencoded"
                    ).action("/api/auth/logout")


##### api router #####

_api_router = APIRouter(prefix="/api", tags=["api"])


# NOTE: aria2 proxy router must be protected by user auth,
# because `AriaNgIframe` expose aria2c rpc-secret in `src` of <iframe>,
# e.g <iframe src="...secret=...">
_aria2_proxy_assembly = _api.aria2.build_aria2_proxy_on(
    APIRouter(dependencies=[Depends(_user_redirect)])
)
_app.on_shutdown(_aria2_proxy_assembly.on_shutdown)
_api_router.include_router(
    _aria2_proxy_assembly.router, prefix="/aria2", tags=["aria2"]
)

_api_router.include_router(_api.auth.auth_router, prefix="/auth", tags=["auth"])
_api_router.include_router(_api.auth.users_router, prefix="/users", tags=["users"])


##### assembly #####

_app.mount("/static/AriaNg", aria_ng_app(FastAPI()), name="AriaNg-static")
_app.include_router(_api_router)
_app.include_router(_gui_router)


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
