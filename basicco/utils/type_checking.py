"""Runtime type checking with support for import paths."""

from itertools import chain
from typing import TYPE_CHECKING

from six import text_type, string_types, integer_types
from six.moves import collections_abc

from .import_path import (
    MODULE_SEPARATOR,
    extract_generic_paths,
    format_import_path,
    import_from_path,
)
from .qualified_name import get_qualified_name
from .unique_iterator import unique_iterator

if TYPE_CHECKING:
    from typing import Any, Iterable, Optional, Tuple, Type, Union

    SingleInputType = Union[Type, str, None]
    InputTypes = Union[SingleInputType, Iterable[SingleInputType]]

    SingleType = Union[Type, str]
    Types = Tuple[SingleType, ...]

__all__ = [
    "TEXT_TYPE",
    "BASE_STRING_TYPES",
    "STRING_TYPES",
    "INTEGER_TYPES",
    "flatten_types",
    "get_type_names",
    "format_types",
    "import_types",
    "is_instance",
    "is_subclass",
    "assert_is_instance",
    "assert_is_subclass",
    "assert_is_callable",
]

TEXT_TYPE = text_type  # type: Type
"""Main text type; `unicode` for Python 2, `str` for Python 3."""

BASE_STRING_TYPES = string_types  # type: Tuple[Type, ...]
"""Base string type."""

STRING_TYPES = tuple({str, TEXT_TYPE})  # type: Tuple[Type, ...]
"""All string types."""

INTEGER_TYPES = integer_types  # type: Tuple[Type, ...]
"""All integer types."""


def flatten_types(types):
    # type: (InputTypes) -> Tuple[SingleType, ...]
    """
    Flatten types into a tuple.

    .. code:: python

        >>> from basicco.utils.type_checking import flatten_types, get_type_names

        >>> get_type_names(flatten_types((int, ("itertools|chain", float, (str,)))))
        ('int', 'chain', 'float', 'str')
        >>> get_type_names(flatten_types(int))
        ('int',)

    :param types: Types.
    :type types: str or type or None or tuple[str or type or None]

    :return: Flattened types.
    :rtype: tuple[str or type]

    :raises TypeError: Invalid types.
    """
    if types is None:
        return (type(None),)
    elif isinstance(types, (string_types, type)):
        return (types,)
    elif isinstance(types, collections_abc.Iterable):
        return tuple(
            unique_iterator(chain.from_iterable(flatten_types(t) for t in types))
        )
    else:
        raise TypeError(type(types).__name__)


def get_type_names(types):
    # type: (InputTypes) -> Tuple[str, ...]
    """
    Get type names without importing from paths. Can be used for user-feedback purposes.

    .. code:: python

        >>> from basicco.utils.type_checking import get_type_names

        >>> get_type_names((int, "itertools|chain"))
        ('int', 'chain')

    :param types: Types.
    :type types: str or type or None or tuple[str or type or None]

    :return: Type names.
    :rtype: tuple[str]
    """
    return tuple(
        MODULE_SEPARATOR.join(extract_generic_paths(t)[0].split(MODULE_SEPARATOR)[-1:])
        if isinstance(t, string_types)
        else (
            get_qualified_name(t, fallback=t.__name__)
            if isinstance(t, type)
            else get_qualified_name(type(t), fallback=type(t).__name__)
        )
        for t in flatten_types(types)
        if t
    )


def format_types(
    types,  # type: InputTypes
    default_module=None,  # type: Optional[str]
    builtin_modules=None,  # type: Optional[Union[str, Iterable[str]]]
):
    # type: (...) -> Types
    """
    Validate input types, add a module path if missing one, resolve relative paths.

    .. code:: python

        >>> from basicco.utils.type_checking import format_types, get_type_names

        >>> get_type_names(format_types((int, "chain"), default_module="itertools"))
        ('int', 'chain')
        >>> get_type_names(format_types(float))
        ('float',)
        >>> get_type_names(format_types("itertools|chain"))
        ('chain',)

    :param types: Types.
    :type types: str or type or None or tuple[str or type or None]

    :param default_module: Default module path (for paths without a module).
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: Formatted types.
    :rtype: tuple[str or type]

    :raises ValueError: Invalid type path/no module provided.
    :raises TypeError: Did not provide valid types.
    """
    return tuple(
        format_import_path(
            t, default_module=default_module, builtin_modules=builtin_modules
        )
        if isinstance(t, string_types)
        else t
        for t in flatten_types(types)
    )


def import_types(
    types,  # type: InputTypes
    default_module=None,  # type: Optional[str]
    builtin_modules=None,  # type: Optional[Union[str, Iterable[str]]]
):
    # type: (...) -> Tuple[Type, ...]
    """
    Import types from lazy import paths.

    .. code:: python

        >>> from basicco.utils.type_checking import import_types, get_type_names

        >>> get_type_names(import_types("itertools|chain"))
        ('chain',)
        >>> get_type_names(import_types(("itertools|chain", "itertools|compress")))
        ('chain', 'compress')

    :param types: Types.
    :type types: str or type or None or tuple[str or type or None]

    :param default_module: Default module path (for paths without a module).
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: Imported types.
    :rtype: tuple[type]
    """
    imported_types = tuple(
        import_from_path(
            t, default_module=default_module, builtin_modules=builtin_modules
        )
        if isinstance(t, string_types)
        else t
        for t in flatten_types(types)
    )
    if len(STRING_TYPES) > 1:
        all_string_types = set(STRING_TYPES)
        if all_string_types.intersection(imported_types):
            imported_types += tuple(all_string_types.difference(imported_types))
    if len(INTEGER_TYPES) > 1:
        all_integer_types = set(INTEGER_TYPES)
        if all_integer_types.intersection(imported_types):
            imported_types += tuple(all_integer_types.difference(imported_types))
    return imported_types


def is_instance(
    obj,  # type: Any
    types,  # type: InputTypes
    subtypes=True,  # type: bool
    default_module=None,  # type: Optional[str]
    builtin_modules=None,  # type: Optional[Union[str, Iterable[str]]]
):
    # type: (...) -> bool
    """
    Get whether object is an instance of any of the provided types.

    .. code:: python

        >>> from itertools import chain
        >>> from basicco.utils.type_checking import is_instance

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
    :type obj: object

    :param types: Types.
    :type types: str or type or None or tuple[str or type or None]

    :param subtypes: Whether to accept subtypes.
    :type subtypes: bool

    :param default_module: Default module path (for paths without a module).
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: True if it is an instance.
    :rtype: bool
    """
    imported_types = import_types(
        types, default_module=default_module, builtin_modules=builtin_modules
    )
    if subtypes:
        return isinstance(obj, imported_types)
    else:
        return type(obj) in imported_types


def is_subclass(
    cls,  # type: Type
    types,  # type: InputTypes
    subtypes=True,  # type: bool
    default_module=None,  # type: Optional[str]
    builtin_modules=None,  # type: Optional[Union[str, Iterable[str]]]
):
    # type: (...) -> bool
    """
    Get whether class is a subclass of any of the provided types.

    .. code:: python

        >>> from itertools import chain
        >>> from basicco.utils.type_checking import is_subclass

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
    :type cls: type

    :param types: Types.
    :type types: str or type or None or tuple[str or type or None]

    :param subtypes: Whether to accept subtypes.
    :type subtypes: bool

    :param default_module: Default module path (for paths without a module).
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: True if it is a subclass.
    :rtype: bool

    :raises TypeError: Did not provide a class.
    """
    if not isinstance(cls, type):
        error = "is_subclass() arg 1 must be a class"
        raise TypeError(error)
    imported_types = import_types(
        types, default_module=default_module, builtin_modules=builtin_modules
    )
    if subtypes:
        return issubclass(cls, import_types(types))
    else:
        return cls in imported_types


def assert_is_instance(
    obj,  # type: Any
    types,  # type: InputTypes
    subtypes=True,  # type: bool
    default_module=None,  # type: Optional[str]
    builtin_modules=None,  # type: Optional[Union[str, Iterable[str]]]
):
    # type: (...) -> None
    """
    Assert object is an instance of any of the provided types.

    .. code:: python

        >>> from itertools import chain
        >>> from basicco.utils.type_checking import assert_is_instance

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
        TypeError: got 'int' object, expected instance of 'chain' or any of its \
subclasses
        >>> assert_is_instance(chain(), "itertools|chain", subtypes=False)
        >>> assert_is_instance(SubChain(), "itertools|chain", subtypes=False)
        Traceback (most recent call last):
        TypeError: got 'SubChain' object, expected instance of 'chain' (instances of \
subclasses are not accepted)

    :param obj: Object.
    :type obj: object

    :param types: Types.
    :type types: str or type or None or tuple[str or type or None]

    :param subtypes: Whether to accept subtypes.
    :type subtypes: bool

    :param default_module: Default module path (for paths without a module).
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :raises ValueError: No types were provided.
    :raises TypeError: Object is not an instance of provided types.
    """
    if not is_instance(
        obj,
        types,
        subtypes=subtypes,
        default_module=default_module,
        builtin_modules=builtin_modules,
    ):
        types = flatten_types(types)
        if not types:
            error = "no types were provided to perform assertion"
            raise ValueError(error)
        error = "got '{}' object, expected instance of {}{}".format(
            type(obj).__name__,
            ", ".join("'{}'".format(name) for name in get_type_names(types)),
            " or any of {} subclasses".format("their" if len(types) > 1 else "its")
            if subtypes
            else " (instances of subclasses are not accepted)",
        )
        raise TypeError(error)


def assert_is_subclass(
    cls,  # type: Type
    types,  # type: InputTypes
    subtypes=True,  # type: bool
    default_module=None,  # type: Optional[str]
    builtin_modules=None,  # type: Optional[Union[str, Iterable[str]]]
):
    # type: (...) -> None
    """
    Assert a class is a subclass of any of the provided types.

    .. code:: python

        >>> from itertools import chain
        >>> from basicco.utils.type_checking import assert_is_subclass

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
    :type cls: type

    :param types: Types.
    :type types: str or type or None or tuple[str or type or None]

    :param subtypes: Whether to accept subtypes.
    :type subtypes: bool

    :param default_module: Default module path (for paths without a module).
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :raises ValueError: No types were provided.
    :raises TypeError: Class is not a subclass of provided types.
    """
    if not is_instance(
        cls, type, default_module=default_module, builtin_modules=builtin_modules
    ):
        types = flatten_types(types)
        error = "got instance of '{}', expected {}{}{}".format(
            type(cls).__name__,
            "one of " if len(types) > 1 else "class ",
            ", ".join("'{}'".format(name) for name in get_type_names(types)),
            " or any of {} subclasses".format("their" if len(types) > 1 else "its")
            if subtypes
            else " (subclasses are not accepted)",
        )
        raise TypeError(error)

    if not is_subclass(
        cls,
        types,
        subtypes=subtypes,
        default_module=default_module,
        builtin_modules=builtin_modules,
    ):
        types = flatten_types(types)
        if not types:
            error = "no types were provided to perform assertion"
            raise ValueError(error)

        error = "got '{}', expected {}{}{}".format(
            cls.__name__,
            "one of " if len(types) > 1 else "class ",
            ", ".join("'{}'".format(name) for name in get_type_names(types)),
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

        >>> from basicco.utils.type_checking import assert_is_subclass

        >>> assert_is_callable(int)
        >>> assert_is_callable(lambda: None)
        >>> assert_is_callable(3)
        Traceback (most recent call last):
        TypeError: got non-callable 'int' object, expected a callable

    :param value: Value.

    :raises TypeError: Value is not a match.
    """
    if not callable(value):
        error = "got non-callable '{}' object, expected a callable".format(
            type(value).__name__,
        )
        raise TypeError(error)
