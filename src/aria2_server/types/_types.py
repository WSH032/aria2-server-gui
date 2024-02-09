from pathlib import Path
from typing import (
    Any,
    Callable,
    Literal,
    TypeVar,
    Union,
)

from nicegui.language import Language as LanguageType

__all__ = (
    "AnyCallable",
    "BoolStr",
    "DecoratedCallable",
    "EndpointDocumentationType",
    "FalseStr",
    "Ipv4HostType",
    "Ipv6HostType",
    "IpvAnyHostType",
    "LanguageType",
    "SqliteDbPathType",
    "TrueStr",
    "UvicornLoggingLevelType",
)

AnyCallable = Callable[..., Any]
DecoratedCallable = TypeVar("DecoratedCallable", bound=AnyCallable)


TrueStr = Literal["true"]
FalseStr = Literal["false"]
BoolStr = Literal[TrueStr, FalseStr]

Ipv4HostType = Literal["127.0.0.1", "0.0.0.0"]
Ipv6HostType = Literal["::1", "::"]
IpvAnyHostType = Literal[Ipv4HostType, Ipv6HostType]
SqliteDbPathType = Union[Path, Literal[":memory:"]]

UvicornLoggingLevelType = Literal[
    "critical", "error", "warning", "info", "debug", "trace"
]

EndpointDocumentationType = Literal["none", "internal", "page", "all"]
