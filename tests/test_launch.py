import asyncio
from typing import Set

from aria2_server.app.main import main
from aria2_server.app.server import Server


def test_main() -> None:
    async def shutdown_app():
        task_set: Set[asyncio.Task[None]] = set()

        async def shutdown_after_server_started():
            # server instance can be accessed only after startup
            server_instance = Server.get_server()
            # wait for server to start, then shutdown it
            while not server_instance.started:
                await asyncio.sleep(0.1)
            Server.app.shutdown()

        # store a strong reference
        task = asyncio.create_task(shutdown_after_server_started())
        task_set.add(task)
        task.add_done_callback(task_set.discard)

    Server.app.on_startup(shutdown_app)  # pyright: ignore[reportUnknownMemberType]
    main()
