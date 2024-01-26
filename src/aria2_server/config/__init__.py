import importlib
import sys
from typing import Optional

from aria2_server.config import schemas
from aria2_server.config.schemas import Config

__all__ = ("GLOBAL_CONFIG", "reload")


_is_loaded = False


def reload(
    config: Optional[schemas.Config] = None, _reload_nicegui: bool = False
) -> Config:
    """This unstable api that only be used internally.

    This function should be called at the very beginning of the program lifecycle,
    **before importing other `aria2_server` modules**,
    and preferably only called once throughout.
    Otherwise, it might fail to fully reload the new config.
    """

    global _is_loaded, GLOBAL_CONFIG

    # When the module is imported for the first time,
    # `_is_loaded` is `False`, so we just return the config to `GLOBAL_CONFIG`.
    # After loaded, `_is_loaded` will be set to `True`,
    # so the next time we call `reload()`, we can execute the following code.
    if not _is_loaded:
        _is_loaded = True
        return Config()

    # NOTE: assign before reloading modules,
    # so that we can reflect the changes to all modules.
    GLOBAL_CONFIG = config if config is not None else Config()  # pyright: ignore[reportConstantRedefinition]

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
