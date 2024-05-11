import ssl
from contextlib import ContextDecorator
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Literal, Optional, Type, TypedDict, Union

import nicegui
import nicegui.server
import nicegui.ui
from fastapi import FastAPI
from nicegui import ui
from typing_extensions import Self

# just import to run the code in that module
import aria2_server.app.server._core  # noqa: F401  # pyright: ignore[reportUnusedImport]
from aria2_server import logger
from aria2_server._types import (
    EndpointDocumentationType,
    IpvAnyHostType,
    LanguageType,
    UvicornLoggingLevelType,
)
from aria2_server.app.server import utils
from aria2_server.config import get_current_config

__all__ = (
    "RunKwargs",
    "RunWithKwargs",
    "app",
    "build_run_kwargs",
    "build_run_with_kwargs",
    "get_server",
    "run",
    "run_with",
    "utils",
)


class _BaseUiKwargs(TypedDict):
    title: str
    favicon: Optional[Union[str, Path]]
    dark: Union[bool, None]
    language: LanguageType
    storage_secret: str


class _UvicornKwargs(TypedDict):
    ssl_keyfile: Optional[str]  # NOTE: not `Path` type, this is uvicorn typing issue
    ssl_certfile: Optional[Path]
    ssl_keyfile_password: Optional[str]
    root_path: str


class RunWithKwargs(_BaseUiKwargs):
    app: FastAPI


class RunKwargs(_UvicornKwargs, _BaseUiKwargs):
    host: IpvAnyHostType
    port: int
    show: bool
    reload: Literal[False]
    uvicorn_logging_level: UvicornLoggingLevelType
    endpoint_documentation: EndpointDocumentationType


def _build_uvivorn_kwargs() -> _UvicornKwargs:
    global_config = get_current_config()

    ########## 👇 ##########
    # we need do some hack for perform typing check,
    # because the typing of following arguments is `*kwargs` in `Server.run`

    # HACK, FIXME: This is uvicorn typing issue
    # We have to convert `ssl_keyfile` to `str` type to make typing happy
    ssl_keyfile = (
        str(global_config.server.ssl_keyfile)
        if global_config.server.ssl_keyfile is not None
        else None
    )
    ssl_certfile = global_config.server.ssl_certfile
    ssl_keyfile_password = (
        global_config.server.ssl_keyfile_password.get_secret_value()
        if global_config.server.ssl_keyfile_password is not None
        else None
    )
    root_path = global_config.server.root_path

    uvicorn_kwargs = _UvicornKwargs(
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        ssl_keyfile_password=ssl_keyfile_password,
        root_path=root_path,
    )

    return uvicorn_kwargs


def _build_base_ui_kwargs(storage_secret: str) -> _BaseUiKwargs:
    global_config = get_current_config()

    base_ui_kwargs = _BaseUiKwargs(
        title=global_config.server.title,
        favicon=global_config.server.favicon,
        dark=global_config.server.dark,
        language=global_config.server.language,
        storage_secret=storage_secret,
    )

    return base_ui_kwargs


def build_run_kwargs(storage_secret: str) -> RunKwargs:
    global_config = get_current_config()
    reload = False

    run_kwargs = RunKwargs(
        host=global_config.server.host,
        port=global_config.server.port,
        uvicorn_logging_level=global_config.server.uvicorn_logging_level,
        reload=reload,
        show=global_config.server.show,
        endpoint_documentation=global_config.server.endpoint_documentation,
        **_build_base_ui_kwargs(storage_secret),
        **_build_uvivorn_kwargs(),
    )

    return run_kwargs


def build_run_with_kwargs(app: FastAPI, storage_secret: str) -> RunWithKwargs:
    run_with_kwargs = RunWithKwargs(app=app, **_build_base_ui_kwargs(storage_secret))

    return run_with_kwargs


if TYPE_CHECKING:
    import uvicorn

    _fake_app = nicegui.app
    _fake_secret = "secret"

    # just for type checking
    uvicorn.Config(app=_fake_app, **_build_uvivorn_kwargs())
    ui.run(**build_run_kwargs(_fake_secret))
    ui.run_with(**build_run_with_kwargs(_fake_app, _fake_secret))


# To performance reasons, we use `ContextDecorator` instead of `asynccontextmanager`,
# because `asynccontextmanager` will create a new generator instance every time it is called.
# see: https://docs.python.org/zh-cn/3/library/contextlib.html#contextlib.asynccontextmanager
class _LogSSLError(ContextDecorator):
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ):
        # error from uvicorn, usually, it's a error because of wrong password of the private key file
        # see: https://github.com/encode/uvicorn/blob/4f74ed144768d53fe6a959683c8e2a9bc51cc00a/uvicorn/config.py#L101-L118
        if exc_type is ssl.SSLError:
            logger.critical(
                f"SSL Error occurred, may be the password of the private key file is wrong.\n{exc_value}"
            )


run = _LogSSLError()(ui.run)
run_with = ui.run_with
app = nicegui.app


def get_server() -> nicegui.server.Server:
    """Accessible only after startup."""
    try:
        return nicegui.server.Server.instance
    except AttributeError:
        raise RuntimeError("Accessible only after startup.") from None
