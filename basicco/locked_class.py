"""Prevents changing public class attributes."""

import six
from tippo import Any

from .mangling import mangle

__all__ = ["LockedClassMeta", "LockedClass"]


class LockedClassMeta(type):
    """Metaclass that prevents changing public class attributes."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(LockedClassMeta, cls).__init__(name, bases, dct, **kwargs)

        # Lock class attributes.
        if not cls.__locked__:
            locked_attr = mangle("__locked", cls.__name__)
            type.__setattr__(cls, locked_attr, True)
            assert cls.__locked__

    def __getattr__(cls, name):
        # type: (str) -> Any
        locked_attr = mangle("__locked", cls.__name__)
        if name == locked_attr:
            type.__setattr__(cls, locked_attr, False)
            return False
        else:
            return cls.__getattribute__(name)

    def __setattr__(cls, name, value):
        """Prevent setting public class attributes."""
        if cls.__locked__ and not name.startswith("_"):
            error = "can't set read-only class attribute {!r}".format(name)
            raise AttributeError(error)
        super(LockedClassMeta, cls).__setattr__(name, value)

    def __delattr__(cls, name):
        """Prevent deleting class attributes."""
        if cls.__locked__ and not name.startswith("_"):
            error = "can't delete read-only class attribute {!r}".format(name)
            raise AttributeError(error)
        super(LockedClassMeta, cls).__delattr__(name)

    @property
    def __locked__(cls):
        # type: () -> bool
        locked_attr = mangle("__locked", cls.__name__)
        return getattr(cls, locked_attr)


class LockedClass(six.with_metaclass(LockedClassMeta, object)):
    """Class that prevents changing public class attributes."""

    __slots__ = ()
