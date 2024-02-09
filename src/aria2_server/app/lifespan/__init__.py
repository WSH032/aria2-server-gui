import asyncio
from contextlib import ExitStack, asynccontextmanager, contextmanager
from textwrap import dedent
from typing import (
    Any,
    Callable,
    ContextManager,
    Generator,
    List,
)

from fastapi_users.exceptions import UserNotExists
from sqlalchemy import exists

from aria2_server import logger
from aria2_server.app._core.aria2 import Aria2WatchdogLifespan
from aria2_server.app._core.auth import UserManager, get_user_manager
from aria2_server.db import get_async_session, migrations
from aria2_server.db.user import get_user_db
from aria2_server.db.user.schemas import UserCreate

__all__ = ("context", "lifespans")


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


async def _check_if_user_existent(
    user_manager: UserManager, *, email: str, password: str
) -> bool:
    """check if a user is existent in the `user_manager`.

    If there exists a user in the `user_manager`
    whose email and password match the arguments, return True;
    otherwise, return False.

    Warning:
        This function can not be used in production environment,
        because it have not considered the security issues.
    """
    try:
        existent_user = await user_manager.get_by_email(email)
    except UserNotExists:
        return False

    is_same_pwd, _ = user_manager.password_helper.verify_and_update(
        password, existent_user.hashed_password
    )

    return is_same_pwd


@contextmanager
def _init_superuser_in_db(*_) -> Generator[None, None, None]:
    async def main():
        get_async_session_context = asynccontextmanager(get_async_session)
        get_user_db_context = asynccontextmanager(get_user_db)
        get_user_manager_context = asynccontextmanager(get_user_manager)

        async with get_async_session_context() as session, get_user_db_context(
            session
        ) as user_db, get_user_manager_context(user_db) as user_manager:
            # If there are not any users in the database, create a default superuser.
            _results = await session.execute(exists(user_db.user_table).select())

            at_least_one_user_existent = _results.scalar_one()
            assert isinstance(at_least_one_user_existent, bool)

            if not at_least_one_user_existent:
                await user_manager.create(_DEFAULT_SUPERUSER)

            # Check if the default superuser exists, if so, issue a security warning.
            email_to_check = _DEFAULT_SUPERUSER.email
            password_to_check = _DEFAULT_SUPERUSER.password

            if await _check_if_user_existent(
                user_manager,
                email=email_to_check,
                password=password_to_check,
            ):
                msg = dedent(
                    f"""\
                    The default user exists in the system, which is a security risk.
                    please change the account as soon as possible.

                    default user:
                    ---
                    email: {email_to_check}
                    password: {password_to_check}
                    ---"""
                )
                logger.warning(msg)

    asyncio.run(main())
    yield


# NOTE: It is best to start aria2c within this lifespan,
# so that users can use aria2c without starting the app.
lifespans: List[_LifespanType] = [
    _init_db,
    _init_superuser_in_db,
    Aria2WatchdogLifespan,
]
"""We provide this list for you to append your own lifespan events,
but you cannot modify the existing events."""


@contextmanager
def context() -> Generator[None, None, None]:
    """Launch the all lifespans in the `lifespans` list."""
    with ExitStack() as stack:
        for lifespan in lifespans:
            stack.enter_context(lifespan())
        yield
