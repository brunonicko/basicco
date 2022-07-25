"""Runtime type checking with support for import paths."""

from __future__ import absolute_import, division, print_function

import itertools

import six
from six import moves
from tippo import TYPE_CHECKING, TypeVar, Mapping, Iterable, get_args, get_origin, cast

from .import_path import DEFAULT_BUILTIN_PATHS, import_path

if TYPE_CHECKING:
    from tippo import Any, Callable, Type

__all__ = [
    "TEXT_TYPES",
    "TypeCheckError",
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

_T = TypeVar("_T")


class TypeCheckError(Exception):
    """Raised when failed to assert type check."""


def _is_typing_form(typ):
    return hasattr(typ, "__module__") and typ.__module__ in ("typing", "typing_extensions")


def _check_union(obj, union, *args):
    union_args = get_args(union)
    if not union_args:
        error = "missing arguments to Union"
        raise TypeError(error)

    for typ in union_args:
        if _check(obj, typ, *args):
            return True

    return False


def _check_type(obj, typ, *args):
    type_args = get_args(typ)
    if not type_args:
        error = "missing arguments to Type"
        raise TypeError(error)
    if len(type_args) != 1:
        error = "unsupported types used in {!r}".format(typ)
        raise TypeError(error)

    is_obj_type = isinstance(obj, type)
    if not is_obj_type:
        return False

    value_type = type_args[0]

    return _check(obj, value_type, False, *args[1:])


def _check_mapping(obj, mapping, *args):
    mapping_args = get_args(mapping)
    is_obj_mapping = _check(obj, six.moves.collections_abc.Mapping, *args)  # type: ignore
    if not mapping_args:
        return is_obj_mapping
    if len(mapping_args) != 2:
        error = "unsupported types used in mapping type {!r}".format(mapping)
        raise TypeError(error)
    if not is_obj_mapping:
        return False

    key_type, value_type = mapping_args
    for key, value in six.iteritems(obj):
        if not _check(key, key_type, *args):
            return False
        if not _check(value, value_type, *args):
            return False

    return True


def _check_iterable(obj, iterable, *args):
    iterable_args = get_args(iterable)
    is_obj_iterable = _check(obj, six.moves.collections_abc.Iterable, *args)  # type: ignore
    if not iterable_args:
        return is_obj_iterable
    if len(iterable_args) != 1:
        error = "unsupported types used in iterable type {!r}".format(iterable)
        raise TypeError(error)
    if not is_obj_iterable:
        return False

    value_type = iterable_args[0]
    for value in obj:
        if not _check(value, value_type, *args):
            return False

    return True


def _check_typing(obj, typ, *args):
    type_name = getattr(typ, "__name__")

    # Any.
    if type_name == "Any":
        return True

    # Union.
    if type_name == "Union":
        return _check_union(obj, typ, *args)

    # Type.
    if type_name == "Type":
        return _check_type(obj, typ, *args)

    # Mapping.
    try:
        type_is_mapping = issubclass(get_origin(typ), Mapping)
    except TypeError:
        type_is_mapping = False
    if type_is_mapping:
        return _check_mapping(obj, typ, *args)

    # Iterable.
    try:
        type_is_iterable = issubclass(get_origin(typ), Iterable)
    except TypeError:
        type_is_iterable = False
    if type_is_iterable:
        return _check_iterable(obj, typ, *args)

    # Unknown type.
    error = "can't check type against {!r}".format(typ)
    raise TypeError(error)


def _check(
    obj,  # type: Any
    typ,  # type: Type | str | None
    instance,  # type: bool
    subtypes,  # type: bool
    extra_paths,  # type: Iterable[str]
    builtin_paths,  # type: Iterable[str]
    generic,  # type: bool
):
    # type: (...) -> bool
    if typ is None:

        # Convert None to NoneType.
        typ = type(None)

    else:

        if isinstance(typ, six.string_types):

            # Lazy path to type.
            typ = import_path(typ, extra_paths=extra_paths, builtin_paths=builtin_paths, generic=generic)

        if not isinstance(typ, type):

            # Not a type, must be a typing form.
            if _is_typing_form(typ):
                return _check_typing(obj, typ, subtypes, instance, extra_paths, builtin_paths, generic)

            # Invalid.
            error = "{!r} object is not a valid type".format(type(typ).__name__)
            raise TypeError(error)

    # Perform simple value check.
    if instance:
        if subtypes:
            return isinstance(obj, typ)
        else:
            return type(obj) is typ
    else:
        if not isinstance(obj, type):
            return False
        if subtypes:
            return issubclass(obj, typ)
        else:
            return obj is typ


def format_types(types):
    # type: (Type| str | None | Iterable[Type| str | None]) -> tuple[Type | str, ...]
    """
    Format types into a tuple.

    :param types: Type(s)/Import Path(s).
    :return: Tuple of Types/Import Paths.
    """
    if types is None:
        return (type(None),)
    elif isinstance(types, type) or isinstance(types, six.string_types) or _is_typing_form(types):
        return (types,)  # type: ignore
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
    type_names_ = []
    for typ in format_types(types):
        if isinstance(typ, six.string_types):
            type_names_.append(typ.split(".")[-1])
        elif isinstance(typ, type):
            type_names_.append(typ.__name__)
        elif _is_typing_form(typ):
            type_names_.append(repr(typ))
        else:
            type_names_.append(type(typ).__name__)
    return tuple(type_names_)


def import_types(
    types,  # type: Type | str | None | Iterable[Type | str | None]
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> tuple[Type, ...]
    """
    Import types from lazy import paths.

    :param types: Types.
    :param extra_paths: Extra module paths in fallback order.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :return: Imported types.
    """
    imported_types = tuple(
        import_path(t, extra_paths=extra_paths, builtin_paths=builtin_paths, generic=generic)
        if isinstance(t, six.string_types)
        else t
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
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> bool
    """
    Get whether object is an instance of the provided types.

    :param obj: Object.
    :param types: Types.
    :param subtypes: Whether to accept subtypes.
    :param extra_paths: Extra module paths in fallback order.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :return: True if it is an instance.
    """
    imported_types = import_types(types, extra_paths=extra_paths, builtin_paths=builtin_paths, generic=generic)
    return any(_check(obj, t, True, subtypes, extra_paths, builtin_paths, generic) for t in imported_types)


def is_subclass(
    cls,  # type: Type
    types,  # type: Type | str | None | Iterable[Type | str | None]
    subtypes=True,  # type: bool
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> bool
    """
    Get whether class is a subclass of the provided types.

    :param cls: Class.
    :param types: Types.
    :param subtypes: Whether to accept subtypes.
    :param extra_paths: Extra module paths in fallback order.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :return: True if it is a subclass.
    :raises TypeError: Did not provide a class.
    """
    if not isinstance(cls, type):
        error = "is_subclass() arg 1 must be a class"
        raise TypeError(error)
    imported_types = import_types(types, extra_paths=extra_paths, builtin_paths=builtin_paths, generic=generic)
    return any(_check(cls, t, False, subtypes, extra_paths, builtin_paths, generic) for t in imported_types)


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
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> _T
    """
    Assert object is an instance of the provided types.

    :param obj: Object.
    :param types: Types.
    :param subtypes: Whether to accept subtypes.
    :param extra_paths: Extra module paths in fallback order.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :raises ValueError: No types were provided.
    :raises TypeCheckError: Object is not an instance of provided types.
    """
    if not is_instance(
        obj,
        types,
        subtypes=subtypes,
        extra_paths=extra_paths,
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
        raise TypeCheckError(error)
    return obj


def assert_is_subclass(
    cls,  # type: Type[_T]
    types,  # type: Type[_T] | str | None | Iterable[Type[_T] | str | None]
    subtypes=True,  # type: bool
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
):
    # type: (...) -> Type[_T]
    """
    Assert a class is a subclass of the provided types.

    :param cls: Class.
    :param types: Types.
    :param subtypes: Whether to accept subtypes.
    :param extra_paths: Extra module paths in fallback order.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :raises ValueError: No types were provided.
    :raises TypeCheckError: Class is not a subclass of provided types.
    """
    if not isinstance(cls, type):
        types = format_types(types)
        error = "got instance of {!r}, expected {}{}{}".format(
            type(cls).__name__,
            "one of " if len(types) > 1 else "class ",
            ", ".join(repr(n) for n in type_names(types)),
            " or any of {} subclasses".format("their" if len(types) > 1 else "its")
            if subtypes
            else " (subclasses are not accepted)",
        )
        raise TypeCheckError(error)

    if not is_subclass(
        cls,
        types,
        subtypes=subtypes,
        extra_paths=extra_paths,
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
        raise TypeCheckError(error)

    return cast("Type[_T]", cls)


def assert_is_callable(value):
    # type: (Callable[..., _T]) -> Callable[..., _T]
    """
    Assert a value is callable.

    :param value: Value.
    :raises TypeCheckError: Value is not a callable.
    """
    if not callable(value):
        error = "got non-callable {!r} object, expected a callable".format(type(value).__name__)
        raise TypeCheckError(error)
    return value


def assert_is_iterable(value, include_strings=False):
    # type: (Iterable[_T], bool) -> Iterable[_T]
    """
    Assert a value is iterable.
    By default, strings are not considered iterables.

    :param value: Value.
    :param include_strings: Whether to consider strings as iterables.
    :raises TypeCheckError: Value is not iterable.
    """
    if not is_iterable(value, include_strings=include_strings):
        error = "got non-iterable {!r} object, expected an iterable".format(type(value).__name__)
        raise TypeCheckError(error)
    return value
