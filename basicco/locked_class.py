"""Prevents changing public class attributes."""

import contextlib

import six
from tippo import Any, Iterator, Type

from .mangling import mangle
from .type_checking import assert_is_instance

__all__ = ["is_locked", "set_locked", "unlocked_context", "LockedClassMeta", "LockedClass"]


def is_locked(cls):
    # type: (Type) -> bool
    """
    Tell whether public attributes of a class are locked or not.

    :param cls: Class.
    :return: True if locked.
    """
    locked_attr = mangle("__locked", cls.__name__)
    try:
        locked = getattr(cls, locked_attr)
    except AttributeError:
        pass
    else:
        return locked
    assert_is_instance(cls, LockedClassMeta)
    raise


def set_locked(cls, locked):
    # type: (Type[LockedClass] | LockedClassMeta, bool) -> None
    """
    Set class locked state.

    :param cls: Class.
    :param locked: Locked state.
    :raise TypeCheckError: Invalid class type.
    """
    locked_attr = mangle("__locked", cls.__name__)
    if not hasattr(cls, locked_attr):
        assert_is_instance(cls, LockedClassMeta)
    type.__setattr__(cls, locked_attr, locked)


@contextlib.contextmanager
def unlocked_context(cls):
    # type: (Type[LockedClass] | LockedClassMeta) -> Iterator
    """
    Unlocked class context manager.

    :param cls: Class.
    :raise TypeCheckError: Invalid class type.
    """
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
        error = "class {!r} has no attribute {!r}".format(cls.__name__, name)
        raise AttributeError(error)

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
