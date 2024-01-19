from functools import partial

from fastapi import FastAPI

from aria2_server.app.core._static_files import (
    StaticFiles,
    bind_static_files_to_app,
)
from aria2_server.static import aria_ng_static_files

__all__ = ("aria_ng_app",)

_aria_ng_static_files_asgi = StaticFiles(directory=aria_ng_static_files, html=True)

aria_ng_app = partial(bind_static_files_to_app, _aria_ng_static_files_asgi)


if __name__ == "__main__":
    from nicegui import app, ui

    app.mount("/AriaNg", aria_ng_app(FastAPI()), name="AriaNg")

    ui.run(reload=False, show=False, uvicorn_logging_level="info")
