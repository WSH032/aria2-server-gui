import functools
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Coroutine,
    Generic,
    TypeVar,
)

import httpx
from fastapi import APIRouter, Request, WebSocket
from fastapi_proxy_lib.core.http import ReverseHttpProxy
from fastapi_proxy_lib.core.websocket import ReverseWebSocketProxy

from aria2_server.config import get_current_config

__all__ = ("build_aria2_proxy_on",)


_RouterTypeVar = TypeVar("_RouterTypeVar", bound=APIRouter)


@dataclass
class _Aria2ProxyAssembly(Generic[_RouterTypeVar]):
    router: _RouterTypeVar
    on_shutdown: Callable[..., Coroutine[Any, Any, None]]


# httpx will automatically set proxy via system proxy settings,
# we forbidden it here, because we will connect to localhost, which does not need proxy.
# ref: https://www.python-httpx.org/advanced/#routing
_proxy_client = httpx.AsyncClient(mounts={"all://": None})


def build_aria2_proxy_on(
    router: _RouterTypeVar,
) -> _Aria2ProxyAssembly[_RouterTypeVar]:
    """

    Args:
        router: please use a new router instance for each call of this function.
            for security reason, please use router with authentication function.

    Returns:
        A on_shutdown callback to close all proxy.
        We return this shutdown event callback instead of set it on router directly,
        because fastapi does not support lifespan on APIRouter level,
        see https://github.com/tiangolo/fastapi/discussions/10464

    ## TODO: set on_shutdown on router directly when fastapi support lifespan on APIRouter level.
    """

    # e.g. localhost:6800
    global_config = get_current_config()

    aria2_netloc = f"localhost:{global_config.aria2.rpc_listen_port}"
    is_secure_rpc = global_config.aria2.rpc_secure == "true"

    # NOTE: DO NOT set `base_url` to `.../jsonrpc/`,
    # because aria2c allow GET method,
    # e.g. /jsonrpc?method=METHOD_NAME&id=ID&params=BASE64_ENCODED_PARAMS

    # e.g. http://localhost:6800/
    http_proto = "https" if is_secure_rpc else "http"
    http_base_url = f"{http_proto}://{aria2_netloc}/"
    aria2_http_proxy = ReverseHttpProxy(_proxy_client, base_url=http_base_url)

    # e.g. ws://localhost:6800/
    ws_proto = "wss" if is_secure_rpc else "ws"
    ws_base_url = f"{ws_proto}://{aria2_netloc}/"
    aria2_ws_proxy = ReverseWebSocketProxy(_proxy_client, base_url=ws_base_url)

    ##########
    #
    # NOTE: DO NOT use `GET` method, because we use cookies to authenticate,
    # `GET` method will cause CSRF issue.
    #
    ##########

    # NOTE: `/rpc-secret` route must be placed before `/{path:path}` route,
    # see https://fastapi.tiangolo.com/tutorial/path-params/#order-matters
    @router.post("/rpc-secret")
    def post_rpc_secret() -> str:  # pyright: ignore[reportUnusedFunction]
        """Return rpc-secret for aria2c."""
        return global_config.aria2.rpc_secret.get_secret_value()

    @router.post("/{path:path}")
    @functools.wraps(aria2_http_proxy.proxy)
    async def aria2_http_endpoint(request: Request, path: str = ""):  # pyright: ignore[reportUnusedFunction]
        return await aria2_http_proxy.proxy(request=request, path=path)

    @router.websocket("/{path:path}")
    @functools.wraps(aria2_ws_proxy.proxy)
    async def aria2_ws_endpoint(websocket: WebSocket, path: str = ""):  # pyright: ignore[reportUnusedFunction]
        return await aria2_ws_proxy.proxy(websocket=websocket, path=path)

    async def on_shutdown(*_: Any, **__: Any) -> None:
        await aria2_http_proxy.aclose()
        await aria2_ws_proxy.aclose()

    return _Aria2ProxyAssembly[_RouterTypeVar](router, on_shutdown)
