"""Decorator that prevents infinite recursion for `__repr__` methods."""

import functools
import threading

import six
from tippo import Callable, Counter, TypeVar, overload

__all__ = ["recursive_repr"]


_T = TypeVar("_T")

_reprs = threading.local()


@overload
def recursive_repr(
    maybe_func,  # type: Callable[..., _T]
    max_depth=1,  # type: int | None
    max_repr="...",  # type: str
):
    # type: (...) -> Callable[..., _T]
    pass


@overload
def recursive_repr(
    maybe_func,  # type: None
    max_depth=1,  # type: int | None
    max_repr="...",  # type: str
):
    # type: (...) -> Callable[[Callable[..., _T]], Callable[..., _T]]
    pass


def recursive_repr(maybe_func=None, max_depth=1, max_repr="..."):
    """
    Decorate a representation method/function to prevent infinite recursion.

    :param maybe_func: The '__repr__' and/or '__str__' method/function or None.
    :param max_depth: Maximum depth.
    :param max_repr: Repr text to return after max depth has been reached.
    :return: Decorated method function or decorator.
    """

    def decorator(func):
        # type: (Callable[..., _T]) -> Callable[..., _T]

        @functools.wraps(func)
        def decorated(*args, **kwargs):

            # Get self (or cls for class methods).
            try:
                self = args[0]
            except IndexError:
                error = "'recursive_repr' needs to decorate a class/instance method"
                exc = RuntimeError(error)
                six.raise_from(exc, None)
                raise exc
            self_id = id(self)

            # Get reprs counter for current context and increment it for self.
            had_reprs = False
            try:
                reprs = _reprs.reprs
            except AttributeError:
                reprs = _reprs.reprs = Counter()
            else:
                had_reprs = True
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
                    del _reprs.reprs[self_id]

                if not had_reprs:
                    del _reprs.reprs

        return decorated

    # Return decorated or decorated.
    if maybe_func is not None:
        return decorator(maybe_func)
    else:
        return decorator
