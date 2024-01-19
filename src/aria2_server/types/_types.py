from typing import (
    Any,
    Callable,
    TypeVar,
)

from typing_extensions import ParamSpec

__all__ = ("AnyCallable", "DecoratedCallable", "P", "R")

AnyCallable = Callable[..., Any]
DecoratedCallable = TypeVar("DecoratedCallable", bound=AnyCallable)

P = ParamSpec("P")
R = TypeVar("R")
