import importlib
import sys
from typing import Optional

from aria2_server.config import schemas

__all__ = ("get_current_config", "reload", "schemas")


_global_config: schemas.Config


def get_current_config() -> schemas.Config:
    """This function always returns the newest global config.

    Warning:
        You should never change the returned global config,
        instead, you should call `reload()` to change the global config.
    """
    try:
        # XXX: maybe we should return `.copy()`,
        # but maybe it will cause performance issue?
        return _global_config
    except NameError:
        raise RuntimeError(
            "The global config has not been initialized yet. "
            f"You should call `{__name__}.{reload.__name__}` first."
        ) from None


def reload(
    config: Optional[schemas.Config] = None,
    _reload_nicegui: bool = True,
) -> None:
    """Initialize or reload the global config.

    This function should be called once before importing other `aria2_server` modules,

    If you want to launch the app again, you should call this function.

    Args:
        config: The config to be loaded.
            If `None`:
                The first time to call `reload()`, it will initialize the global config.
                The second time or later to call `reload()`, it just refresh all the modules,
                so that you can launch the whole app again.
            If not `None`:
                It will change the global config to the new one.
        _reload_nicegui: Whether to reload `nicegui` module when refreshing.
            Usually, you should set it to `True`, so that you can launch the whole app again.
            The argument is private, we keep it here just for debugging purpose.
    """

    global _global_config

    try:
        # just to check whether `_global_config` is defined
        _global_config  # noqa: B018 # pyright: ignore[reportUnusedExpression]
    except NameError:
        # The first time to call `reload()`
        # i.e. `_global_config` is not defined
        _global_config = config if config is not None else schemas.Config()
    else:
        # The second time or later to call `reload()`
        if config is not None:
            _global_config = config

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
