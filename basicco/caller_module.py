"""Retrieve the caller's module name."""

import functools
import inspect

import six
from tippo import Callable, Iterable, TypeVar

__all__ = ["caller_module", "auto_caller_module"]


T = TypeVar("T")


def caller_module(frames=0):
    # type: (int) -> str | None
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
                return frame[0].f_globals["__name__"]
            except (IndexError, KeyError):
                return None
        else:
            return module.__name__


def auto_caller_module(
    iterable_params=None,  # type: Iterable[str] | str | None
    single_params=None,  # type: Iterable[str] | str | None
):
    # type: (...) -> Callable[[T], T]
    """
    Make a decorator for a function that takes iterable/single keyword arguments that contain module paths.
    If no paths are provided, set the caller module as a path.

    :param iterable_params: Keyword arguments that are supposed to contain module paths.
    :param single_params: Keyword argument that are supposed to contain a single module path or None.
    :return: Decorator.
    """
    if isinstance(iterable_params, six.string_types):
        iterable_params = (iterable_params,)
    elif iterable_params is None:
        iterable_params = ()
    else:
        iterable_params = tuple(iterable_params)

    if isinstance(single_params, six.string_types):
        single_params = (single_params,)
    elif single_params is None:
        single_params = ()
    else:
        single_params = tuple(single_params)

    def decorator(func):
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            _iterable_params = []
            _single_params = []
            for iterable_param in iterable_params:
                values = tuple(kwargs.get(iterable_param, ()))
                if not values:
                    _iterable_params.append(iterable_param)
            for single_param in single_params:
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
