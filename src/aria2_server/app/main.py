import asyncio

from aria2_server.app.lifespan import Lifespan
from aria2_server.app.server import Server
from aria2_server.config import GLOBAL_CONFIG

__all__ = ("main",)


def main() -> None:
    with Lifespan.context():
        server_config_in_db = asyncio.run(Server.utils.get_server_config_from_db())

        storage_secret = server_config_in_db.secret_token
        reload = False

        # NOTE: Don't unpack `GLOBAL_CONFIG` outside of a function
        Server.run(
            host=GLOBAL_CONFIG.server.host,
            port=GLOBAL_CONFIG.server.port,
            title=GLOBAL_CONFIG.server.title,
            dark=GLOBAL_CONFIG.server.dark,
            language=GLOBAL_CONFIG.server.language,
            storage_secret=storage_secret,
            uvicorn_logging_level=GLOBAL_CONFIG.server.uvicorn_logging_level,
            reload=reload,
            show=GLOBAL_CONFIG.server.show,
            endpoint_documentation=GLOBAL_CONFIG.server.endpoint_documentation,
            favicon=GLOBAL_CONFIG.server.favicon,
        )


if __name__ == "__main__":
    main()
