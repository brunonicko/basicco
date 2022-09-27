"""Prevents changing public class attributes."""

import contextlib

import six
from tippo import Any, Iterator, Type

from .mangling import mangle

__all__ = ["is_locked", "set_locked", "unlocked_context", "LockedClassMeta", "LockedClass"]


def is_locked(cls):
    # type: (Type) -> bool
    locked_attr = mangle("__locked", cls.__name__)
    return getattr(cls, locked_attr)


def set_locked(cls, locked):
    # type: (Type, bool) -> None
    locked_attr = mangle("__locked", cls.__name__)
    type.__setattr__(cls, locked_attr, locked)


@contextlib.contextmanager
def unlocked_context(cls):
    # type: (Type) -> Iterator
    before = is_locked(cls)
    if before:
        set_locked(cls, False)
    try:
        yield
    finally:
        if before:
            set_locked(cls, True)


class LockedClassMeta(type):
    """Metaclass that prevents changing public class attributes."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(LockedClassMeta, cls).__init__(name, bases, dct, **kwargs)
        if not is_locked(cls):
            set_locked(cls, True)

    def __getattr__(cls, name):
        # type: (str) -> Any
        locked_attr = mangle("__locked", cls.__name__)
        if name == locked_attr:
            type.__setattr__(cls, locked_attr, False)
            return False
        try:
            return super(LockedClassMeta, cls).__getattr__(name)  # type: ignore  # noqa
        except AttributeError:
            pass
        return cls.__getattribute__(name)

    def __setattr__(cls, name, value):
        """Prevent setting public class attributes."""
        if is_locked(cls) and not name.startswith("_"):
            error = "can't set read-only class attribute {!r}".format(name)
            raise AttributeError(error)
        super(LockedClassMeta, cls).__setattr__(name, value)

    def __delattr__(cls, name):
        """Prevent deleting class attributes."""
        if is_locked(cls) and not name.startswith("_"):
            error = "can't delete read-only class attribute {!r}".format(name)
            raise AttributeError(error)
        super(LockedClassMeta, cls).__delattr__(name)


class LockedClass(six.with_metaclass(LockedClassMeta, object)):
    """Class that prevents changing public class attributes."""

    __slots__ = ()
