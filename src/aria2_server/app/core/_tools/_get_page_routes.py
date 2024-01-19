from typing import List

from fastapi.routing import APIRoute
from nicegui import app
from nicegui.client import Client

from aria2_server.types._types import AnyCallable

__all__ = ("get_page_routes",)


def get_page_routes(endpoint: AnyCallable) -> List[APIRoute]:
    route_path = Client.page_routes.get(endpoint)
    if route_path is not None:
        return [
            route
            for route in app.routes
            if isinstance(route, APIRoute)
            and route.methods == {"GET"}
            and route.path == route_path
        ]

    raise RuntimeError("Route not found")
