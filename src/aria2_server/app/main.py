import asyncio

from aria2_server.app import server
from aria2_server.app.lifespan import Lifespan

__all__ = ("main",)


def main() -> None:
    with Lifespan.context():
        server_config_in_db = asyncio.run(server.utils.get_server_config_in_db())

        server.run(**server.build_run_kwargs(server_config_in_db.secret_token))


if __name__ == "__main__":
    main()
