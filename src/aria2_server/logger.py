"""The logger module for `aria2_server`.

NOTE: This module will never import any other modules in `aria2_server`,
    So, any other modules can import this module to use the logger.
"""

import functools
import logging
from typing import Any, Callable, TypeVar

import typer
from typing_extensions import Concatenate, ParamSpec

# NOTE: DO NOT import any `aria2_server` modules here,
# because any other modules may import this module to use the logger.

__all__ = (
    "LOGGER_NAME",
    "configure_default_logging",
    "critical",
    "debug",
    "error",
    "exception",
    "info",
    "logger",
    "use_colors",
    "warning",
)


_P = ParamSpec("_P")
_R = TypeVar("_R")


LOGGER_NAME = "aria2_server"

# DO NOT add any handler or set the level of the logger here,
# do them in `aria2_server.cli` instead.
# see: https://docs.python.org/3/howto/logging-cookbook.html#adding-handlers-other-than-nullhandler-to-a-logger-in-a-library
logger: logging.Logger = logging.getLogger(LOGGER_NAME)


use_colors: bool = True
"""The flag to control whether to use ANSI color codes in the log messages."""


# Ref: https://github.com/encode/uvicorn/blob/4f74ed144768d53fe6a959683c8e2a9bc51cc00a/uvicorn/logging.py#L23-L32
_debug_colorizer = functools.partial(typer.style, fg=typer.colors.CYAN)
_info_colorizer = functools.partial(typer.style, fg=typer.colors.GREEN)
_warning_colorizer = functools.partial(typer.style, fg=typer.colors.YELLOW)
_error_colorizer = functools.partial(typer.style, fg=typer.colors.RED)
_critical_colorizer = functools.partial(typer.style, fg=typer.colors.BRIGHT_RED)


# NOTE: we use this factory function,
# instead of directly:
# ```py
# def debug(...) -> None:
#    ...
#    return logger.debug(...)
# ```
# it's for the type hint of the wrapped function which is returned by this factory function.
def _build_colorized_logger_func(
    logger_func: Callable[Concatenate[str, _P], _R],
) -> Callable[Concatenate[Any, _P], _R]:
    """The factory function can make `logger_func` colorized.

    Note:
        This function can only be used internally.

    Example:
        ```python
        # In this module
        debug = _build_colorized_log_func(logger.debug)

        # Then, the `debug` will automatically add ANSI color codes to the message.
        ```
    """
    logger_func_to_colorizer = {
        logger.debug: _debug_colorizer,
        logger.info: _info_colorizer,
        logger.warning: _warning_colorizer,
        logger.error: _error_colorizer,
        logger.exception: _error_colorizer,
        logger.critical: _critical_colorizer,
    }
    _: Any = logger_func  # HACK: make typing happy
    colorizer = logger_func_to_colorizer.get(_)

    # Usually, if this function is only used internally, the `colorizer` should not be None.
    assert (
        colorizer is not None
    ), "The `logger_function` must be a method of `aria2_server.logging.logger`."

    @functools.wraps(logger_func)
    def wrapped_logger_func(msg: Any, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        colorized_msg = colorizer(msg) if use_colors else msg
        return logger_func(colorized_msg, *args, **kwargs)

    return wrapped_logger_func


debug = _build_colorized_logger_func(logger.debug)
info = _build_colorized_logger_func(logger.info)
warning = _build_colorized_logger_func(logger.warning)
error = _build_colorized_logger_func(logger.error)
exception = _build_colorized_logger_func(logger.exception)
critical = _build_colorized_logger_func(logger.critical)


def configure_default_logging(level: int) -> None:
    """Configure the default logging settings for `aria2_server`.

    Usually, this function is used by cli.
    """
    logging.basicConfig(
        level=level,
        format="%(levelname)-5.5s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
