"""Utility to get mro bases."""

import collections
import inspect

from tippo import GenericMeta, Type

__all__ = ["get_mro"]


def get_mro(cls):
    # type: (Type) -> tuple[Type, ...]
    """
    Get consistent mro amongst different python versions.
    This works even with generic classes.

    :param cls: Class.
    :return: Tuple of classes.
    """

    # Resolve generic class to its origin.
    generic = cls
    while hasattr(generic, "__origin__"):
        generic = getattr(generic, "__origin__")
        if generic is not None:
            cls = generic

    # Newer python versions.
    if GenericMeta is type:
        return tuple(inspect.getmro(cls))

    # Special logic to skip generic classes when GenericMeta is being used, for old python.
    mro = collections.deque()  # type: collections.deque[Type]
    for base in reversed(inspect.getmro(cls)):
        generic = base
        origin = None
        while hasattr(generic, "__origin__"):
            generic = getattr(generic, "__origin__")
            if generic is not None:
                origin = generic
        if origin in mro:
            continue
        mro.appendleft(base)
    return tuple(mro)
