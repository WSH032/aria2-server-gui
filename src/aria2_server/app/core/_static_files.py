from typing import Any, TypeVar

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from starlette.staticfiles import StaticFiles as StarletteStaticFiles

__all__ = ("StaticFiles", "bind_static_files_to_app")

_AppType = TypeVar("_AppType", bound=FastAPI)


class StaticFiles(StarletteStaticFiles):
    assert not hasattr(StarletteStaticFiles, "get_response_for_request")

    async def get_response_for_request(self, request: Request) -> Response:
        # modified from:
        #     https://github.com/encode/starlette/blob/3734e85c187a22e30c5ba3530a4f4506912f8eec/starlette/staticfiles.py#L94-L106
        scope = request.scope

        if not self.config_checked:
            await self.check_config()
            self.config_checked = True

        return await self.get_response(self.get_path(scope), scope)


def bind_static_files_to_app(
    static_files: StaticFiles, app: _AppType, *args: Any, **kwargs: Any
) -> _AppType:
    """Must mounted as app, not as router.

    Examples:
        ```py
        bind_static_files_to_app(StaticFiles(), FastAPI())
        ```
    """

    # NOTE: `{path:path}` is necessary
    # ref: https://www.starlette.io/routing/#path-parameters
    #      https://fastapi.tiangolo.com/tutorial/path-params/#path-convertor
    # NOTE: must mounted as app, not as router
    #      It is because `StaticFiles` is actually an app
    @app.get("/{path:path}", *args, **kwargs)
    async def _(request: Request) -> Response:
        return await static_files.get_response_for_request(request)

    return app
