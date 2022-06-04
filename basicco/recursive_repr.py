"""Decorator that prevents infinite recursion for `__repr__` methods."""

import collections
import functools
import contextvars
from typing import Callable, Optional, Union, TypeVar, overload
from typing import Counter as TCounter

try:
    from typing import Literal
except ImportError:
    Literal = Union  # type: ignore

__all__ = ["recursive_repr"]


_T = TypeVar("_T")

_reprs: contextvars.ContextVar[TCounter[int]] = contextvars.ContextVar("_reprs")


@overload
def recursive_repr(
    maybe_func: Callable[..., _T],
    max_depth: Optional[int] = 1,
    max_repr: str = "...",
) -> Callable[..., _T]:
    pass


@overload
def recursive_repr(
    maybe_func: Literal[None],
    max_depth: Optional[int] = 1,
    max_repr: str = "...",
) -> Callable[[Callable[..., _T]], Callable[..., _T]]:
    pass


def recursive_repr(maybe_func=None, max_depth=1, max_repr="..."):
    """
    Decorate a representation method/function to prevent infinite recursion.

    :param maybe_func: The '__repr__' and/or '__str__' method/function or None.
    :param max_depth: Maximum depth.
    :param max_repr: Repr text to return after max depth has been reached.
    :return: Decorated method function or decorator.
    """

    def decorator(func: Callable[..., _T]) -> Callable[..., _T]:
        @functools.wraps(func)
        def decorated(*args, **kwargs):

            # Get self (or cls for class methods).
            try:
                self = args[0]
            except IndexError:
                raise RuntimeError("'recursive_repr' needs to decorate a class/instance method") from None
            self_id = id(self)

            # Get reprs counter for current context and increment it for self.
            reprs_token = None
            try:
                reprs = _reprs.get()
            except LookupError:
                reprs = collections.Counter()
                reprs_token = _reprs.set(reprs)
            reprs[self_id] += 1

            # Return representation.
            try:
                if max_depth is not None and reprs[self_id] > max_depth:
                    return max_repr
                else:
                    return func(*args, **kwargs)
            finally:

                # Decrement repr counter and clean up if needed.
                reprs[self_id] -= 1
                if not reprs[self_id]:
                    del reprs[self_id]

                if reprs_token is not None:
                    _reprs.reset(reprs_token)

        return decorated

    # Return decorated or decorated.
    if maybe_func is not None:
        return decorator(maybe_func)
    else:
        return decorator
