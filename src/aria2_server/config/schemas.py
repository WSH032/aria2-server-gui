import secrets
from pathlib import Path
from typing import Literal, Optional, Union

from nicegui.language import Language
from nicegui.native import find_open_port
from pydantic import BaseModel, ConfigDict, Field, FilePath, SecretStr

from aria2_server.static import favicon

__all__ = ("Aria2", "Config", "Server")

_Ipv4HostType = Literal["127.0.0.1", "0.0.0.0"]
_Ipv6HostType = Literal["::1", "::"]
_IpvAnyHostType = Literal[_Ipv4HostType, _Ipv6HostType]
_SqliteDbPathType = Union[Path, Literal[":memory:"]]

_LOWEST_PORT = 1024
_HIGHEST_PORT = 65535

_DEFAULT_EXPIRATION_SECOND = 60 * 60 * 24 * 7  # 7 days
_DEFAULT_DB_PATH = Path("db.sqlite3")


class _ConfigedBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True, validate_default=True)


class Aria2(_ConfigedBaseModel):
    # https://aria2.github.io/manual/en/html/aria2c.html
    rpc_listen_all: bool = False
    rpc_listen_port: int = Field(
        default_factory=lambda: find_open_port(6800, 7800),
        ge=_LOWEST_PORT,
        le=_HIGHEST_PORT,
    )
    rpc_secret: SecretStr = Field(default_factory=secrets.token_urlsafe)
    conf_path: Optional[FilePath] = None


class Server(_ConfigedBaseModel):
    host: _IpvAnyHostType = "0.0.0.0"
    port: int = Field(default=7800, ge=_LOWEST_PORT, le=_HIGHEST_PORT)
    title: str = "Aria2-Server"
    dark: Optional[bool] = None
    show: bool = True
    language: Language = "en-US"
    uvicorn_logging_level: Literal[
        "critical", "error", "warning", "info", "debug", "trace"
    ] = "warning"
    endpoint_documentation: Literal["none", "internal", "page", "all"] = "page"
    favicon: Path = favicon

    sqlite_db: _SqliteDbPathType = _DEFAULT_DB_PATH
    expiration_second: int = Field(default=_DEFAULT_EXPIRATION_SECOND, gt=0)

    aria2: Aria2 = Aria2()


class Config(_ConfigedBaseModel):
    server: Server = Server()
