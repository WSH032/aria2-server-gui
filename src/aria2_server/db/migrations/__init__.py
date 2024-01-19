from functools import partial
from pathlib import Path

from alembic import command, config
from sqlalchemy import Connection

from aria2_server.db._core import DATABASE_URL, engine
from aria2_server.db.base import Base

__all__ = (
    "alembic_ini",
    "script_location",
    "get_default_cfg",
    "upgrade",
    "revision",
    "run_async_upgrade",
)

_here = Path(__file__).parent

alembic_ini = _here / "alembic.ini"
assert alembic_ini.exists()

script_location = _here / "alembic"
assert script_location.exists()


def get_default_cfg() -> config.Config:
    cfg = config.Config(alembic_ini)
    cfg.set_main_option("script_location", str(script_location))
    cfg.set_main_option("sqlalchemy.url", str(DATABASE_URL))
    cfg.attributes["target_metadata"] = Base.metadata
    return cfg


upgrade = partial(command.upgrade, config=get_default_cfg(), revision="head")

revision = partial(command.revision, config=get_default_cfg(), autogenerate=True)


async def run_async_upgrade() -> None:
    # Refer: https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio
    def run_upgrade(connection: Connection, cfg: config.Config) -> None:
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")

    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, get_default_cfg())
