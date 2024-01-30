import asyncio
from contextlib import ExitStack, asynccontextmanager, contextmanager
from typing import (
    Any,
    Callable,
    ClassVar,
    ContextManager,
    Generator,
    List,
)

from sqlalchemy import exists

from aria2_server.app.core._aria2 import Aria2WatchdogLifespan
from aria2_server.app.core._auth import get_user_manager
from aria2_server.app.core._tools import NamepaceMixin
from aria2_server.db import get_async_session, migrations
from aria2_server.db.user import get_user_db
from aria2_server.db.user.schemas import UserCreate

__all__ = ("Lifespan",)


_LifespanType = Callable[[], ContextManager[Any]]

_DEFAULT_SUPERUSER = UserCreate(
    email="aria2@server.com",
    password="admin",
    is_active=True,
    is_superuser=True,
    is_verified=True,
)


@contextmanager
def _init_db(*_) -> Generator[None, None, None]:
    asyncio.run(migrations.run_async_upgrade())
    yield


@contextmanager
def _init_superuser_in_db(*_) -> Generator[None, None, None]:
    async def main():
        get_async_session_context = asynccontextmanager(get_async_session)
        get_user_db_context = asynccontextmanager(get_user_db)
        get_user_manager_context = asynccontextmanager(get_user_manager)

        async with get_async_session_context() as session, get_user_db_context(
            session
        ) as user_db, get_user_manager_context(user_db) as user_manager:
            results = await session.execute(exists(user_db.user_table).select())

            is_existent = results.scalar_one()
            assert isinstance(is_existent, bool)

            if not is_existent:
                await user_manager.create(_DEFAULT_SUPERUSER)

    asyncio.run(main())
    yield


class Lifespan(NamepaceMixin):
    # NOTE: It is best to start aria2c within this lifespan,
    # so that users can use aria2c without starting the app.
    lifespans: ClassVar[List[_LifespanType]] = [
        _init_db,
        _init_superuser_in_db,
        Aria2WatchdogLifespan,
    ]

    @classmethod
    @contextmanager
    def context(cls) -> Generator[None, None, None]:
        with ExitStack() as stack:
            for lifespan in cls.lifespans:
                stack.enter_context(lifespan())
            yield
