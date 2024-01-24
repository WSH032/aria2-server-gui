import logging
import os
from pathlib import Path
from typing import Optional

import tomli
from pydantic import ValidationError

from aria2_server.config import schemas
from aria2_server.config.schemas import Config

__all__ = ("CONFIG_ENV", "GLOBAL_CONFIG", "reload", "schemas")

CONFIG_ENV = "ARIA2_SERVER_CONFIG"


def _load_config_from_file(file: Path):
    try:
        with file.open("rb") as f:
            toml_dict = tomli.load(f)
    except tomli.TOMLDecodeError as e:
        logging.critical(f"Config file {file} is not a valid TOML file\n{e}")
        raise

    try:
        return Config.model_validate(toml_dict)
    except ValidationError as e:
        logging.critical(f"Config file {file} is not a valid config file\n{e}")
        raise


def _load_config() -> Config:
    _config_env_value = os.getenv(CONFIG_ENV)
    if _config_env_value is not None:
        _config_path = Path(_config_env_value)
        if not _config_path.is_file():
            raise ValueError(
                f"Config file {_config_path}, which is set via environment var, does not exist"
            )
        return _load_config_from_file(Path(_config_env_value))
    return Config()


_is_loaded = False


def reload(
    config: Optional[schemas.Config] = None, _reload_nicegui: bool = False
) -> Config:
    """This unstable api that only be used internally."""
    import importlib
    import sys

    global _is_loaded, GLOBAL_CONFIG

    # When the module is imported for the first time,
    # `_is_loaded` is `False`, so we just return the config to `GLOBAL_CONFIG`.
    # After loaded, `_is_loaded` will be set to `True`,
    # so the next time we call `reload()`, we can execute the following code.
    if not _is_loaded:
        _is_loaded = True
        return _load_config()

    # NOTE: assign before reloading modules,
    # so that we can reflect the changes to all modules.
    GLOBAL_CONFIG = config if config is not None else _load_config()  # pyright: ignore[reportConstantRedefinition]

    modules_name_need_reload = ["aria2_server"]
    if _reload_nicegui:
        modules_name_need_reload.append("nicegui")

    modules_need_reload = [
        module
        for module_name, module in sys.modules.copy().items()
        if module_name.startswith(tuple(modules_name_need_reload))
    ]
    for module in modules_need_reload:
        importlib.reload(module)

    # NOTE: when reloading, the `_is_loaded` will be reset to `False`,
    # so remember to set it to `True` again.
    _is_loaded = True
    return GLOBAL_CONFIG


# https://docs.python.org/3/library/importlib.html#importlib.reload
# Do some magic to skip `GLOBAL_CONFIG = reload()` when reloading this module,
# so that we can re-set `GLOBAL_CONFIG` by `Global GLOBAL_CONFIG = ...` in `reload()`,
try:
    GLOBAL_CONFIG  # type: ignore # noqa: B018
except NameError:
    # following code will be executed when this module is imported for the first time,
    # and will not be executed when this module is reloaded
    GLOBAL_CONFIG = reload()
