"""Utilities to get the MRO that work with generic classes in older Python versions."""

import collections
import inspect

from tippo import Any, Deque, Dict, GenericMeta, Tuple, Type, cast

from basicco.unique_iterator import unique_iterator

__all__ = ["resolve_origin", "get_bases", "get_mro", "preview_mro"]


def resolve_origin(cls):
    # type: (Type[Any]) -> Type[Any]
    """
    Resolve origin for generic alias.

    :param cls: Class or generic alias.
    :return: Original class.
    """
    if hasattr(cls, "__mro_entries__"):
        return cast(Type[Any], cls.__mro_entries__(())[0])
    assert isinstance(cls, type)
    generic = cls
    while hasattr(generic, "__origin__"):
        generic = getattr(generic, "__origin__")
        if generic is not None:
            cls = generic
    return cls


def get_bases(cls):
    # type: (Type[Any]) -> Tuple[Type[Any], ...]
    """
    Get consistent bases amongst different python versions.
    This works even with generic classes.

    :param cls: Class.
    :return: Tuple of classes.
    """

    # Resolve generic class to its origin.
    cls = resolve_origin(cls)

    # Newer python versions.
    if GenericMeta is type:
        return cls.__bases__

    # Return unique bases' origins.
    return tuple(unique_iterator(resolve_origin(b) for b in cls.__bases__))


def get_mro(cls):
    # type: (Type[Any]) -> Tuple[Type[Any], ...]
    """
    Get consistent mro amongst different python versions.
    This works even with generic classes.

    :param cls: Class.
    :return: Tuple of classes.
    """

    # Resolve generic class to its origin.
    cls = resolve_origin(cls)

    # Newer python versions.
    if GenericMeta is type:
        return tuple(inspect.getmro(cls))

    # Special logic to skip generic classes when GenericMeta is being used (old python).
    mro = collections.deque()  # type: Deque[Type[Any]]
    for base in reversed(inspect.getmro(cls)):
        origin = resolve_origin(base)
        if origin in mro:
            continue
        mro.appendleft(base)
    return tuple(mro)


def _build_dummy_bases(
    bases,  # type: Tuple[Type[Any], ...]
    dummy_map,  # type: Dict[Type[Any], Type[Any]]
    base_map,  # type: Dict[Type[Any], Type[Any]]
):
    # type: (...) -> Tuple[Type[Any], ...]
    dummy_bases = []
    for base in bases:
        # Reuse dummy base.
        if base in base_map:
            dummy_bases.append(base_map[base])
            continue

        # Make dummy base.
        if base is object or base is type:
            dummy_base = base
        else:
            dummy_base = type.__new__(
                type,
                base.__name__,
                _build_dummy_bases(base.__bases__, dummy_map, base_map),
                {},
            )

        # Remember and append dummy base.
        dummy_map[dummy_base] = base
        base_map[base] = dummy_base
        dummy_bases.append(dummy_base)

    return tuple(dummy_bases)


def preview_mro(*bases):
    # type: (*Type[Any]) -> Tuple[Type[Any], ...]
    """
    Preview the mro before building the actual class.

    :param bases: Bases.
    :return: Tuple of classes.
    """
    dummy_map = {}  # type: Dict[Type[Any], Type[Any]]
    base_map = {}  # type: Dict[Type[Any], Type[Any]]
    dummy_bases = _build_dummy_bases(bases, dummy_map, base_map)
    dummy_cls = type.__new__(type, "Dummy", dummy_bases, {})
    return tuple(dummy_map[b] for b in get_mro(dummy_cls)[1:])
