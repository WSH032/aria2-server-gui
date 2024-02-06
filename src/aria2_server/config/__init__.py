import importlib
import sys
from typing import Optional

from aria2_server.config import schemas
from aria2_server.config.schemas import Config

__all__ = ("GLOBAL_CONFIG", "reload", "schemas")


_is_loaded = False


def reload(
    config: Optional[schemas.Config] = None, _reload_nicegui: bool = True
) -> Config:
    """This unstable api that only be used internally.

    This function should be called at the very beginning of the program lifecycle,
    **before importing other `aria2_server` modules**,
    and preferably only called once throughout.
    Otherwise, it might fail to fully reload the new config.

    If you want to launch the app again, you should call this function.

    Args:
        config: The new config to be reloaded. If `None`, will reload the default config.
            If you just want to reload for launch the app again, you should pass the previous config.
            e.g. `reload(config.GLOBAL_CONFIG)`
        _reload_nicegui: Whether to reload `nicegui` module.
            Usually, you should set it to `True`, so that you can launch the whole app again.
            The argument is private, we keep it here just for debugging purpose.
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

    # TODO: There is another way to reload `nicegui`,
    # See https://github.com/zauberzeug/nicegui/blob/9dd03ee9d09d506e5504a0d03d349b22cd61d699/nicegui/testing/conftest.py#L54-L77

    # NOTE: Reload the module consistently with the order it was imported.
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
    GLOBAL_CONFIG  # noqa: B018  # pyright: ignore[reportUnusedExpression, reportUnboundVariable]
except NameError:
    # following code will be executed when this module is imported for the first time,
    # and will not be executed when this module is reloaded
    GLOBAL_CONFIG = reload()
