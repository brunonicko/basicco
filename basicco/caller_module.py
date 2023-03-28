"""Retrieve the caller's module name."""

import functools
import inspect

import six
from tippo import Any, Callable, Iterable, Tuple, TypeVar, Union, cast

__all__ = ["caller_module", "auto_caller_module"]


_T = TypeVar("_T")
_RT = TypeVar("_RT")


def caller_module(frames=0):
    # type: (int) -> Union[str, None]
    """
    Get caller module name if possible.

    :param frames: How many frames to go back.
    :return: Module name or None.
    """
    try:
        frame = inspect.stack()[2 + frames]
        module = inspect.getmodule(frame[0])
    except IndexError:
        return None
    else:
        if module is None:
            try:
                return cast(Union[str, None], frame[0].f_globals["__name__"])
            except (IndexError, KeyError):
                return None
        else:
            return module.__name__


def auto_caller_module(
    iterable_params=None,  # type: Union[Iterable[str], str, None]
    single_params=None,  # type: Union[Iterable[str], str, None]
):
    # type: (...) -> Callable[[Callable[..., _T]], Callable[..., _T]]
    """
    Make a decorator for a function that takes iterable/single keyword arguments that
    contain module paths. If no paths are provided, set the caller module as a path.

    :param iterable_params: Keyword arguments that contain module paths.
    :param single_params: Keyword argument that contain a single module path or None.
    :return: Decorator.
    """
    if isinstance(iterable_params, six.string_types):
        iterable_params_ = (iterable_params,)  # type: Tuple[str, ...]
    elif iterable_params is None:
        iterable_params_ = ()
    else:
        iterable_params_ = tuple(iterable_params)

    if isinstance(single_params, six.string_types):
        single_params_ = (single_params,)  # type: Tuple[str, ...]
    elif single_params is None:
        single_params_ = ()
    else:
        single_params_ = tuple(single_params)

    def decorator(func):
        # type: (Callable[..., _RT]) -> Callable[..., _RT]

        @functools.wraps(func)
        def decorated(*args, **kwargs):
            # type: (*Any, **Any) -> Any
            _iterable_params = []
            _single_params = []
            for iterable_param in iterable_params_:
                values = tuple(kwargs.get(iterable_param, ()))
                if not values:
                    _iterable_params.append(iterable_param)
            for single_param in single_params_:
                value = kwargs.get(single_param, None)
                if value is None:
                    _single_params.append(single_param)

            if _iterable_params or _single_params:
                module = caller_module()
                for iterable_param in _iterable_params:
                    kwargs[iterable_param] = (module,)
                for single_param in _single_params:
                    kwargs[single_param] = module

            return func(*args, **kwargs)

        return decorated

    return decorator
