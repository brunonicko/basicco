"""Runtime type checking with support for import paths."""

from __future__ import absolute_import, division, print_function

import itertools

import six
from six import moves
from tippo import TYPE_CHECKING, TypeVar

from .import_path import DEFAULT_BUILTIN_PATHS, import_path

if TYPE_CHECKING:
    from tippo import Any, Callable, Iterable, Type

__all__ = [
    "TEXT_TYPES",
    "type_names",
    "format_types",
    "import_types",
    "is_instance",
    "is_subclass",
    "is_iterable",
    "assert_is_instance",
    "assert_is_subclass",
    "assert_is_callable",
    "assert_is_iterable",
]


_T = TypeVar("_T")
TEXT_TYPES = tuple({str, six.text_type})  # type: tuple[Type, ...]


def format_types(types):
    # type: (Type| str | None | Iterable[Type| str | None]) -> tuple[Type | str, ...]
    """
    Format types into a tuple.

    :param types: Type(s)/Import Path(s).
    :return: Tuple of Types/Import Paths.
    """
    if types is None:
        return (type(None),)
    elif isinstance(types, type) or isinstance(types, six.string_types):
        return (types,)
    elif isinstance(types, moves.collections_abc.Iterable):  # type: ignore
        return tuple(itertools.chain.from_iterable(format_types(t) for t in types))
    else:
        error = "{!r} object is not a valid type".format(type(types).__name__)
        raise TypeError(error)


def type_names(types):
    # type: (Type | str | None | Iterable[Type | str | None]) -> tuple[str, ...]
    """
    Get type names without importing from paths. Can be used for user-feedback purposes.

    :param types: Types.
    :return: Type names.
    """
    return tuple(
        t.split(".")[-1] if isinstance(t, six.string_types) else t.__name__ if isinstance(t, type) else type(t).__name__
        for t in format_types(types)
    )


def import_types(
    types,  # type: Type | str | None | Iterable[Type | str | None]
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> tuple[Type, ...]
    """
    Import types from lazy import paths.

    :param types: Types.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :return: Imported types.
    """
    imported_types = tuple(
        import_path(t, builtin_paths=builtin_paths, generic=generic) if isinstance(t, six.string_types) else t
        for t in format_types(types)
    )

    # Expand all text types.
    if len(TEXT_TYPES) > 1:
        text_types = set(TEXT_TYPES)
        if text_types.intersection(imported_types):
            imported_types += tuple(text_types.difference(imported_types))

    # Expand all integer types.
    if len(six.integer_types) > 1:
        integer_types = set(six.integer_types)
        if integer_types.intersection(imported_types):
            imported_types += tuple(integer_types.difference(imported_types))

    return imported_types


def is_instance(
    obj,  # type: Any
    types,  # type: Type | str | None | Iterable[Type | str | None]
    subtypes=True,  # type: bool
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> bool
    """
    Get whether object is an instance of the provided types.

    :param obj: Object.
    :param types: Types.
    :param subtypes: Whether to accept subtypes.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :return: True if it is an instance.
    """
    imported_types = import_types(types, builtin_paths=builtin_paths, generic=generic)
    if subtypes:
        return isinstance(obj, imported_types)
    else:
        return type(obj) in imported_types


def is_subclass(
    cls,  # type: Type
    types,  # type: Type | str | None | Iterable[Type | str | None]
    subtypes=True,  # type: bool
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> bool
    """
    Get whether class is a subclass of the provided types.

    :param cls: Class.
    :param types: Types.
    :param subtypes: Whether to accept subtypes.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :return: True if it is a subclass.
    :raises TypeError: Did not provide a class.
    """
    if not isinstance(cls, type):
        error = "is_subclass() arg 1 must be a class"
        raise TypeError(error)
    imported_types = import_types(types, builtin_paths=builtin_paths, generic=generic)
    if subtypes:
        return issubclass(cls, import_types(types))
    else:
        return cls in imported_types


def is_iterable(value, include_strings=False):
    # type: (Any, bool) -> bool
    """
    Tell whether a value is an iterable or not.
    By default, strings are not considered iterables.

    :param value: Value.
    :param include_strings: Whether to consider strings as iterables.
    :return: True if iterable.
    """
    return isinstance(value, moves.collections_abc.Iterable) and (  # type: ignore
        (not isinstance(value, six.string_types) or include_strings)
    )


def assert_is_instance(
    obj,  # type: _T
    types,  # type: Type[_T] | str | None | Iterable[Type[_T] | str | None]
    subtypes=True,  # type: bool
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> _T
    """
    Assert object is an instance of the provided types.

    :param obj: Object.
    :param types: Types.
    :param subtypes: Whether to accept subtypes.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :raises ValueError: No types were provided.
    :raises TypeError: Object is not an instance of provided types.
    """
    if not is_instance(
        obj,
        types,
        subtypes=subtypes,
        builtin_paths=builtin_paths,
        generic=generic,
    ):
        types = format_types(types)
        if not types:
            error = "no types were provided to perform assertion"
            raise ValueError(error)
        error = "got {!r} object, expected instance of {}{}".format(
            type(obj).__name__,
            ", ".join(repr(n) for n in type_names(types)),
            " or any of {} subclasses".format("their" if len(types) > 1 else "its")
            if subtypes
            else " (instances of subclasses are not accepted)",
        )
        raise TypeError(error)
    return obj


def assert_is_subclass(
    cls,  # type: Type[_T]
    types,  # type: Type[_T] | str | None | Iterable[Type[_T] | str | None]
    subtypes=True,  # type: bool
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> Type[_T]
    """
    Assert a class is a subclass of the provided types.

    :param cls: Class.
    :param types: Types.
    :param subtypes: Whether to accept subtypes.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :raises ValueError: No types were provided.
    :raises TypeError: Class is not a subclass of provided types.
    """
    if not is_instance(cls, type, builtin_paths=builtin_paths, generic=generic):
        types = format_types(types)
        error = "got instance of {!r}, expected {}{}{}".format(
            type(cls).__name__,
            "one of " if len(types) > 1 else "class ",
            ", ".join(repr(n) for n in type_names(types)),
            " or any of {} subclasses".format("their" if len(types) > 1 else "its")
            if subtypes
            else " (subclasses are not accepted)",
        )
        raise TypeError(error)

    if not is_subclass(
        cls,
        types,
        subtypes=subtypes,
        builtin_paths=builtin_paths,
        generic=generic,
    ):
        types = format_types(types)
        if not types:
            error = "no types were provided to perform assertion"
            raise ValueError(error)

        error = "got {!r}, expected {}{}{}".format(
            cls.__name__,
            "one of " if len(types) > 1 else "class ",
            ", ".join(repr(n) for n in type_names(types)),
            " or any of {} subclasses".format("their" if len(types) > 1 else "its")
            if subtypes
            else " (subclasses are not accepted)",
        )
        raise TypeError(error)

    return cls


def assert_is_callable(value):
    # type: (Callable[..., _T]) -> Callable[..., _T]
    """
    Assert a value is callable.

    :param value: Value.
    :raises TypeError: Value is not a callable.
    """
    if not callable(value):
        error = "got non-callable {!r} object, expected a callable".format(type(value).__name__)
        raise TypeError(error)
    return value


def assert_is_iterable(value, include_strings=False):
    # type: (Iterable[_T], bool) -> Iterable[_T]
    """
    Assert a value is iterable.
    By default, strings are not considered iterables.

    :param value: Value.
    :param include_strings: Whether to consider strings as iterables.
    :raises TypeError: Value is not iterable.
    """
    if not is_iterable(value, include_strings=include_strings):
        error = "got non-iterable {!r} object, expected an iterable".format(type(value).__name__)
        raise TypeError(error)
    return value
