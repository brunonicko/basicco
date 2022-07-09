"""Runtime type checking with support for import paths."""

from __future__ import absolute_import, division, print_function

import itertools

import six
from six import moves
from tippo import TYPE_CHECKING

from .import_path import DEFAULT_BUILTIN_PATHS, import_path

if TYPE_CHECKING:
    from tippo import Any, Iterable, Type

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


TEXT_TYPES = tuple({str, six.text_type})  # type: tuple[Type, ...]


def format_types(types):
    # type: (Type | str | None | Iterable[Type | str | None]) -> tuple[Type | str, ...]
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
        raise TypeError(type(types).__name__)


def type_names(types):
    # type: (Type | str | None | Iterable[Type | str | None]) -> tuple[str, ...]
    """
    Get type names without importing from paths. Can be used for user-feedback purposes.

    .. code:: python
        >>> from basicco.type_checking import type_names
        >>> type_names((int, "itertools.chain"))
        ('int', 'chain')

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

    .. code:: python
        >>> from basicco.type_checking import import_types, type_names
        >>> type_names(import_types("itertools|chain"))
        ('chain',)
        >>> type_names(import_types(("itertools|chain", "itertools|compress")))
        ('chain', 'compress')

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
    Get whether object is an instance of any of the provided types.

    .. code:: python
        >>> from itertools import chain
        >>> from basicco.type_checking import is_instance
        >>> class SubChain(chain):
        ...     pass
        ...
        >>> is_instance(3, int)
        True
        >>> is_instance(3, (chain, int))
        True
        >>> is_instance(3, ())
        False
        >>> is_instance(SubChain(), "itertools|chain")
        True
        >>> is_instance(chain(), "itertools|chain", subtypes=False)
        True
        >>> is_instance(SubChain(), "itertools|chain", subtypes=False)
        False

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
    Get whether class is a subclass of any of the provided types.

    .. code:: python
        >>> from itertools import chain
        >>> from basicco.type_checking import is_subclass
        >>> class SubChain(chain):
        ...     pass
        ...
        >>> is_subclass(int, int)
        True
        >>> is_subclass(int, (chain, int))
        True
        >>> is_subclass(int, ())
        False
        >>> is_subclass(SubChain, "itertools|chain")
        True
        >>> is_subclass(chain, "itertools|chain", subtypes=False)
        True
        >>> is_subclass(SubChain, "itertools|chain", subtypes=False)
        False

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
    obj,  # type: Any
    types,  # type: Type | str | None | Iterable[Type | str | None]
    subtypes=True,  # type: bool
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> None
    """
    Assert object is an instance of any of the provided types.

    .. code:: python
        >>> from itertools import chain
        >>> from basicco.type_checking import assert_is_instance
        >>> class SubChain(chain):
        ...     pass
        ...
        >>> assert_is_instance(3, int)
        >>> assert_is_instance(3, (chain, int))
        >>> assert_is_instance(3, ())
        Traceback (most recent call last):
        ValueError: no types were provided to perform assertion
        >>> assert_is_instance(3, "itertools|chain")
        Traceback (most recent call last):
        TypeError: got 'int' object, expected instance of 'chain' or any of its subclasses
        >>> assert_is_instance(chain(), "itertools|chain", subtypes=False)
        >>> assert_is_instance(SubChain(), "itertools|chain", subtypes=False)
        Traceback (most recent call last):
        TypeError: got 'SubChain' object, expected instance of 'chain' (instances of subclasses are not accepted)

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
            ", ".join("{!r}".format(name) for name in type_names(types)),
            " or any of {} subclasses".format("their" if len(types) > 1 else "its")
            if subtypes
            else " (instances of subclasses are not accepted)",
        )
        raise TypeError(error)


def assert_is_subclass(
    cls,  # type: Type
    types,  # type: Type | str | None | Iterable[Type | str | None]
    subtypes=True,  # type: bool
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> None
    """
    Assert a class is a subclass of any of the provided types.

    .. code:: python
        >>> from itertools import chain
        >>> from basicco.type_checking import assert_is_subclass
        >>> class SubChain(chain):
        ...     pass
        ...
        >>> assert_is_subclass(int, int)
        >>> assert_is_subclass(int, (chain, int))
        >>> assert_is_subclass(int, ())
        Traceback (most recent call last):
        ValueError: no types were provided to perform assertion
        >>> assert_is_subclass(int, "itertools|chain")
        Traceback (most recent call last):
        TypeError: got 'int', expected class 'chain' or any of its subclasses
        >>> assert_is_subclass(chain, "itertools|chain", subtypes=False)
        >>> assert_is_subclass(SubChain, "itertools|chain", subtypes=False)
        Traceback (most recent call last):
        TypeError: got 'SubChain', expected class 'chain' (subclasses are not accepted)

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
            ", ".join("{!r}".format(name) for name in type_names(types)),
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
            ", ".join("{!r}".format(name) for name in type_names(types)),
            " or any of {} subclasses".format("their" if len(types) > 1 else "its")
            if subtypes
            else " (subclasses are not accepted)",
        )
        raise TypeError(error)


def assert_is_callable(value):
    # type: (Any) -> None
    """
    Assert a value is callable.

    .. code:: python
        >>> from basicco.type_checking import assert_is_subclass
        >>> assert_is_callable(int)
        >>> assert_is_callable(lambda: None)
        >>> assert_is_callable(3)
        Traceback (most recent call last):
        TypeError: got non-callable 'int' object, expected a callable

    :param value: Value.
    :raises TypeError: Value is not a callable.
    """
    if not callable(value):
        error = "got non-callable {!r} object, expected a callable".format(type(value).__name__)
        raise TypeError(error)


def assert_is_iterable(value, include_strings=False):
    # type: (Any, bool) -> None
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
