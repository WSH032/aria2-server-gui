from typing import Optional

from fastapi import HTTPException, WebSocketException, status
from fastapi.requests import HTTPConnection
from fastapi.security import APIKeyCookie
from typing_extensions import override

__all__ = ("ConnAPIKeyCookie",)


class ConnAPIKeyCookie(APIKeyCookie):
    """We override the APIKeyCookie class for WebSocket support.

    See: https://github.com/tiangolo/fastapi/pull/10147

    TODO, FIXME, HACK: Remove this override when the PR is merged and released.
    """

    @override
    async def __call__(self, conn: HTTPConnection) -> Optional[str]:
        # Modified: https://github.com/tiangolo/fastapi/blob/141e34f281ed746431766d712d56d357e306a689/fastapi/security/api_key.py#L292-L301
        api_key = conn.cookies.get(self.model.name)
        if not api_key and self.auto_error:
            msg = "Not authenticated"
            scope_type = conn.scope.get("type")
            if scope_type == "websocket":
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION, reason=msg
                )
            elif scope_type == "http":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=msg,
                )
            else:
                raise AssertionError("Unknown scope type")
        return api_key
