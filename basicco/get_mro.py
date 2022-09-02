"""Utility to get mro bases."""

import inspect

import tippo

__all__ = ["get_mro"]


def get_mro(cls):
    # type: (type) -> tuple[type, ...]
    """
    Get consistent mro amongst different python versions.
    This works even with generic classes.

    :param cls: Class.
    :return: Tuple of classes.
    """
    if not hasattr(tippo, "GenericMeta"):
        return tuple(inspect.getmro(cls))

    # Special logic to skip generic classes when GenericMeta is being used, old python.
    mro = []
    for base in inspect.getmro(cls):
        generic = cls
        origin = None
        while hasattr(generic, "__origin__"):
            generic = getattr(generic, "__origin__")
            if generic is not None:
                origin = generic
        if origin in mro:
            continue
        mro.append(base)
    return tuple(mro)
