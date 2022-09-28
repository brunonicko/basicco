"""Decorator that prevents `__repr__` methods from raising exceptions and return a default representation instead."""

import functools
import traceback

from tippo import Callable, overload

__all__ = ["default_alternative_repr", "safe_repr"]


_in_repr = False


def default_alternative_repr(obj):
    # type: (object) -> str
    message = [ln.strip(" ") for ln in traceback.format_exc().split("\n") if ln.strip(" ")][-1]
    return "{}; repr failed due to {!r}>".format(object.__repr__(obj)[:-1], message)


@overload
def safe_repr(
    maybe_func,  # type: Callable[[object], str]
    alternative_repr=default_alternative_repr,  # type: Callable[[object], str]
):
    # type: (...) -> Callable[[object], str]
    pass


@overload
def safe_repr(
    maybe_func,  # type: None
    alternative_repr=default_alternative_repr,  # type: Callable[[object], str]
):
    # type: (...) -> Callable[[Callable[[object], str]], Callable[[object], str]]
    pass


def safe_repr(maybe_func=None, alternative_repr=default_alternative_repr):
    """
    Decorate a representation method/function to prevent infinite recursion.

    :param maybe_func: The '__repr__' and/or '__str__' method/function or None.
    :param alternative_repr: Alternative repr function in case the decorated one fails.
    :return: Decorated method function or decorator.
    """

    def decorator(func):
        # type: (Callable[[object], str]) -> Callable[[object], str]

        @functools.wraps(func)
        def decorated(self, *args, **kwargs):
            global _in_repr
            before = _in_repr
            if not before:
                _in_repr = True
            try:
                return func(self, *args, **kwargs)  # noqa
            except Exception:  # noqa
                if before:
                    raise
                return alternative_repr(self, *args, **kwargs)  # noqa
            finally:
                if not before:
                    _in_repr = False

        return decorated

    # Return decorated or decorated.
    if maybe_func is not None:
        return decorator(maybe_func)
    else:
        return decorator
