import inspect
from functools import wraps
from inspect import Parameter
from typing import Callable, Literal, Sequence, Tuple

from aria2_server.types._types import P, R

__all__ = ("make_args_required",)

_KeywordParamKindType = Literal[
    Parameter.KEYWORD_ONLY,
    Parameter.VAR_KEYWORD,
    Parameter.POSITIONAL_OR_KEYWORD,
]


def make_args_required(
    func: Callable[P, R],
    required_args: Sequence[Tuple[str, _KeywordParamKindType]],
    use_wraps: bool = True,
) -> Callable[P, R]:
    func_parameters = inspect.signature(func).parameters

    for required_param_name, required_param_kind in required_args:
        required_func_param = func_parameters.get(required_param_name)
        assert (
            required_func_param is not None
        ), f"`{required_param_name}` is not a param of `{func.__name__}`"
        assert required_func_param.kind == required_param_kind

    def wrapped_func(*args: P.args, **kwargs: P.kwargs) -> R:
        for required_param_name, _ in required_args:
            if required_param_name not in kwargs:
                raise RuntimeError(
                    f"`{required_param_name}` is required for `{func.__name__}`, please set it"
                )
        return func(*args, **kwargs)

    if use_wraps:
        wraps(func)(wrapped_func)

    return wrapped_func
