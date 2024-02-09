import secrets
from pathlib import Path
from textwrap import dedent
from typing import Optional

from nicegui.native import find_open_port
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, FilePath, SecretStr
from typing_extensions import Annotated

from aria2_server.static import favicon
from aria2_server.types._types import (
    BoolStr,
    EndpointDocumentationType,
    IpvAnyHostType,
    LanguageType,
    SqliteDbPathType,
    TrueStr,
    UvicornLoggingLevelType,
)

__all__ = ("Aria2", "Config", "Server", "ServerExtra")


_LOWEST_PORT = 1024
_HIGHEST_PORT = 65535
_FIND_LOWEST_PORT = 6800
_FIND_HIGHEST_PORT = 7800

_DEFAULT_HOST: IpvAnyHostType = "0.0.0.0"
_DEFAULT_PORT = _FIND_HIGHEST_PORT
_DEFAULT_TITLE = "Aria2-Server"

_DEFAULT_EXPIRATION_SECOND = 60 * 60 * 24 * 7  # 7 days
_DEFAULT_DB_PATH: SqliteDbPathType = Path("aria2-server.db")

_UVICORN_HTTPS_DOCS_URL = "https://www.uvicorn.org/deployment/#running-with-https"
_NICEGUI_RUN_DOCS_URL = "https://nicegui.io/documentation/run#ui_run"


def _check_root_path(value: str) -> str:
    if value == "":
        return value
    if value.endswith("/"):
        raise ValueError("must not end with '/'")
    if not value.startswith("/"):
        raise ValueError("must start with '/'")
    return value


class _ConfigedBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True, validate_default=True, extra="forbid")


class Aria2(_ConfigedBaseModel):
    model_config = ConfigDict(
        title="The cli args of aria2c",
        alias_generator=lambda field_name: field_name.replace("_", "-"),
    )

    # https://aria2.github.io/manual/en/html/aria2c.html
    rpc_listen_all: Annotated[
        BoolStr,
        Field(
            description=dedent(
                """\
                If 'true', aria2c will listen on ipv4 '0.0.0.0' and ipv6 '::'.
                Usually, prefer to set it as 'false', because aria2-server will create a reverse proxy for aria2c."""
            ),
        ),
    ] = "false"
    # TODO: Can not use `Annotated`, see https://github.com/pydantic/pydantic/issues/6713
    rpc_listen_port: int = Field(
        default_factory=lambda: find_open_port(_FIND_LOWEST_PORT, _FIND_HIGHEST_PORT),
        ge=_LOWEST_PORT,
        le=_HIGHEST_PORT,
        description=dedent(
            f"""\
            aria2c will listen on this port. Default is a random port between {_FIND_LOWEST_PORT} and {_FIND_HIGHEST_PORT}.
            Usually, prefer to keep it as default, because aria2-server will create a reverse proxy for aria2c.."""
        ),
    )
    # TODO: Can not use `Annotated`, see https://github.com/pydantic/pydantic/issues/6713
    rpc_secret: SecretStr = Field(
        default_factory=secrets.token_urlsafe,
        description=dedent(
            """\
            The rpc-secret of aria2c. Default is a random string.
            Usually, prefer to keep it as default, and get the secret from aria2-server's API."""
        ),
    )
    rpc_secure: Annotated[
        BoolStr,
        Field(
            description=dedent(
                """\
            If 'true', aria2c will listen on https.
            Usually, prefer to set it as 'false', because aria2-server will create a reverse proxy for aria2c."""
            ),
        ),
    ] = "false"
    # 👆 The above three properties will be used for aria2p in the future,
    # do not change them.
    #
    # 👇 following properties just remind user don't set them in `aria2.conf`
    # because we need these setting to initialize our modules,
    # and we will set them as cli args.
    enable_rpc: Annotated[
        TrueStr,
        Field(
            description=dedent(
                """Can only be 'true', which means enable a JSON-RPC/XML-RPC server of aria2c."""
            ),
        ),
    ] = "true"
    conf_path: Annotated[
        Optional[FilePath],
        Field(
            description=dedent(
                """\
                The path of aria2.conf.
                See <https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-conf-path>"""
            )
        ),
    ] = None


class ServerExtra(_ConfigedBaseModel):
    model_config = ConfigDict(
        title="The extra server config for aria2-server",
    )

    sqlite_db: Annotated[
        SqliteDbPathType,
        Field(
            description="The path of aria2-server's sqlite db file. If ':memory:', will create a in-memory db.",
        ),
    ] = _DEFAULT_DB_PATH
    expiration_second: Annotated[
        int,
        Field(
            gt=0,
            description="The expiration seconds of the token of aria2-server's user auth.",
        ),
    ] = _DEFAULT_EXPIRATION_SECOND


class Server(_ConfigedBaseModel):
    model_config = ConfigDict(
        title=dedent(
            f"""\
            The server config for aria2-server.
            You can refer to <{_NICEGUI_RUN_DOCS_URL}> for most of the properties."""
        ),
    )

    # `nicegui.ui.run`
    host: Annotated[
        IpvAnyHostType, Field(description="The host of aria2-server")
    ] = _DEFAULT_HOST
    port: Annotated[
        int,
        Field(
            ge=_LOWEST_PORT, le=_HIGHEST_PORT, description="The port of aria2-server"
        ),
    ] = _DEFAULT_PORT
    title: Annotated[
        str, Field(description="The default web document title of aria2-server")
    ] = _DEFAULT_TITLE
    dark: Annotated[
        Optional[bool],
        Field(
            description=dedent(
                """\
                For web page visitor, the default dark mode.
                If 'None', will use the system theme. If 'False', will use light theme. If 'True', will use dark theme."""
            )
        ),
    ] = None
    show: Annotated[
        bool,
        Field(
            description="Whether to open the browser automatically after the server starts"
        ),
    ] = True
    language: Annotated[
        LanguageType,
        Field(description="The quasar language theme of aria2-server."),
    ] = "en-US"
    uvicorn_logging_level: Annotated[
        UvicornLoggingLevelType,
        Field(
            description=dedent(
                """\
                The logging level of uvicorn server.
                See <https://www.uvicorn.org/settings/#logging>"""
            )
        ),
    ] = "warning"
    endpoint_documentation: Annotated[
        EndpointDocumentationType,
        Field(
            description=dedent(
                f"""\
                control what endpoints appear in the autogenerated OpenAPI docs.
                See <{_NICEGUI_RUN_DOCS_URL}>"""
            )
        ),
    ] = "page"
    favicon: Annotated[
        Path,
        Field(description="The path of the web favicon file of aria2-server."),
    ] = favicon

    # kwargs of `nicegui.ui.run`
    ssl_keyfile: Annotated[
        Optional[FilePath],
        Field(
            description=dedent(
                f"""\
                The path of the ssl key file of aria2-server, Required for enable https.
                See <{_UVICORN_HTTPS_DOCS_URL}>"""
            )
        ),
    ] = None
    ssl_certfile: Annotated[
        Optional[FilePath],
        Field(
            description=dedent(
                f"""\
                The path of the ssl cert file of aria2-server, Required for enable https.
                See <{_UVICORN_HTTPS_DOCS_URL}>"""
            )
        ),
    ] = None
    ssl_keyfile_password: Annotated[
        Optional[SecretStr],
        Field(
            description=dedent(
                """\
                The password of the ssl key file.
                See <https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_cert_chain>"""
            )
        ),
    ] = None
    root_path: Annotated[
        str,
        Field(
            description=dedent(
                """\
                Set the ASGI root_path for applications submounted below a given URL path.
                If the String is not '', it must start with '/' and not end with '/'.
                See <https://fastapi.tiangolo.com/advanced/behind-a-proxy/>"""
            ),
            examples=["", "/aria2-server"],
        ),
        AfterValidator(_check_root_path),
    ] = ""

    # extra config for aria2-server
    extra: ServerExtra = ServerExtra()


class Config(_ConfigedBaseModel):
    model_config = ConfigDict(
        title="The global config of aria2-server",
    )

    server: Server = Server()
    aria2: Aria2 = Aria2()


if __name__ == "__main__":
    import json

    print(json.dumps(Config.model_json_schema(), indent=4))
