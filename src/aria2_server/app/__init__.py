import asyncio

from aria2_server.app import lifespan, server

__all__ = ("main",)


def main() -> None:
    with lifespan.context():
        server_config_in_db = asyncio.run(server.utils.get_server_config_in_db())

        server.run(**server.build_run_kwargs(server_config_in_db.secret_token))


if __name__ == "__main__":
    main()
