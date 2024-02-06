from fastapi.requests import HTTPConnection

__all__ = ("get_root_path",)


async def get_root_path(conn: HTTPConnection) -> str:
    return conn.scope.get("root_path", "")
