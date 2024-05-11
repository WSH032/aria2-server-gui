from pathlib import Path

from alembic import command, config
from sqlalchemy import Connection

from aria2_server.db._core import get_current_db_url, get_global_engine
from aria2_server.db.base import Base

__all__ = (
    "alembic_ini",
    "get_current_cfg",
    "run_async_upgrade",
    "script_location",
)

_here = Path(__file__).parent

alembic_ini = _here / "alembic.ini"
assert alembic_ini.exists()

script_location = _here / "_alembic"
assert script_location.exists()


def get_current_cfg() -> config.Config:
    """This function returns the current alembic config according to the current global config"""
    cfg = config.Config(alembic_ini)
    cfg.set_main_option("script_location", str(script_location))
    cfg.set_main_option("sqlalchemy.url", get_current_db_url())
    cfg.attributes["target_metadata"] = Base.metadata
    return cfg


async def run_async_upgrade() -> None:
    # Refer: https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio
    def run_upgrade(connection: Connection, cfg: config.Config) -> None:
        cfg.attributes["connection"] = connection
        # NOTE: `no_logging_config` is a custom option used by `aria2-server`,
        # see `env.py` for more details.
        cfg.set_main_option("no_logging_config", "true")
        command.upgrade(cfg, "head")

    async with get_global_engine().begin() as conn:
        current_cfg = get_current_cfg()
        await conn.run_sync(run_upgrade, current_cfg)
