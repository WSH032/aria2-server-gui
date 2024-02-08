import asyncio
import ssl
from typing import TYPE_CHECKING

from aria2_server import logger
from aria2_server.app.lifespan import Lifespan
from aria2_server.app.server import Server
from aria2_server.config import GLOBAL_CONFIG

__all__ = ("main",)


def main() -> None:
    with Lifespan.context():
        ########## 👇 ##########
        # we need do some hack for perform typing check,
        # because the typing of following arguments is `*kwargs` in `Server.run`

        # HACK, FIXME: This is uvicorn typing issue
        # We have to convert `ssl_keyfile` to `str` type to make typing happy
        ssl_keyfile = (
            str(GLOBAL_CONFIG.server.ssl_keyfile)
            if GLOBAL_CONFIG.server.ssl_keyfile is not None
            else None
        )
        ssl_certfile = GLOBAL_CONFIG.server.ssl_certfile
        ssl_keyfile_password = (
            GLOBAL_CONFIG.server.ssl_keyfile_password.get_secret_value()
            if GLOBAL_CONFIG.server.ssl_keyfile_password is not None
            else None
        )
        root_path = GLOBAL_CONFIG.server.root_path

        if TYPE_CHECKING:
            import uvicorn

            uvicorn.Config(
                app="I don't care, just for typing check",
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile,
                ssl_keyfile_password=ssl_keyfile_password,
                root_path=root_path,
            )

        ########## 👆 ##########

        server_config_in_db = asyncio.run(Server.utils.get_server_config_from_db())

        storage_secret = server_config_in_db.secret_token
        reload = False

        try:
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
                # 👇 kwargs for uvicorn.run
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile,
                ssl_keyfile_password=ssl_keyfile_password,
                root_path=root_path,
            )
        except ssl.SSLError as e:
            logger.critical(
                f"SSL Error occurred, may be the password of the private key file is wrong.\n{e}"
            )
            raise


if __name__ == "__main__":
    main()
