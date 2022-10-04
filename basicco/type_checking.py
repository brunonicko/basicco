"""Runtime type checking with support for import paths and type hints."""

import itertools

import six
import typing_inspect  # type: ignore
from tippo import (
    Any,
    Callable,
    ForwardRef,
    Iterable,
    Mapping,
    Type,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_typing,
)

from .import_path import get_name, import_path

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


def _check_literal(obj, literal, type_depth, *args):
    return any(_check(obj, type(v), type_depth, *args) if type_depth else obj == v for v in get_args(literal))


def _check_union(obj, union, *args):
    return any(_check(obj, t, *args) for t in get_args(union))


def _check_type(obj, typ, type_depth, *args):
    if not isinstance(obj, type):
        return False

    type_args = get_args(typ)
    if not type_args:
        return True

    assert len(type_args) == 1
    value_type = type_args[0]
    type_depth += 1

    return _check(obj, value_type, type_depth, *args)


def _check_tuple(obj, typed_tuple, type_depth, instance, *args):
    if type_depth or not instance:
        return _check(obj, tuple, type_depth, instance, *args)

    if not isinstance(obj, tuple):
        return False

    tuple_args = get_args(typed_tuple)
    if not tuple_args:
        return True

    if tuple_args[-1] == Ellipsis:
        if len(tuple_args) == 1:
            return True
        typ = tuple_args[0]
        return all(_check(v, typ, type_depth, instance, *args) for v in obj)

    if len(obj) != len(tuple_args):
        return False

    return all(_check(v, t, type_depth, instance, *args) for v, t in zip(obj, tuple_args))


def _check_mapping(obj, mapping, type_depth, instance, typing, *args):
    origin = get_origin(mapping)
    if type_depth or not instance:
        return _check(obj, origin, type_depth, instance, False, *args)

    if not isinstance(obj, origin):
        return False

    mapping_args = get_args(mapping)
    if not mapping_args:
        return True

    assert len(mapping_args) == 2
    key_type, value_type = mapping_args
    for key, value in six.iteritems(obj):
        if not _check(key, key_type, type_depth, instance, typing, *args):
            return False
        if not _check(value, value_type, type_depth, instance, typing, *args):
            return False

    return True


def _check_iterable(obj, iterable, type_depth, instance, typing, *args):
    origin = get_origin(iterable)
    if type_depth or not instance:
        return _check(obj, origin, type_depth, instance, False, *args)

    if not isinstance(obj, origin):
        return False

    iterable_args = get_args(iterable)
    if not iterable_args:
        return True

    assert len(iterable_args) == 1
    value_type = iterable_args[0]
    for value in obj:
        if not _check(value, value_type, type_depth, instance, typing, *args):
            return False

    return True


def _check_forward_ref(
    obj,
    forward_ref,
    type_depth,
    instance,
    typing,
    subtypes,
    extra_paths,
    builtin_paths,
    generic,
):
    typ = import_path(
        forward_ref.__forward_arg__,
        extra_paths=extra_paths,
        builtin_paths=builtin_paths,
        generic=generic,
    )
    return _check(
        obj,
        typ,
        type_depth,
        instance,
        typing,
        subtypes,
        extra_paths,
        builtin_paths,
        generic,
    )


def _check_typing(
    obj,
    typ,
    type_depth,
    instance,
    typing,
    subtypes,
    extra_paths,
    builtin_paths,
    generic,
):
    args = (
        type_depth,
        instance,
        typing,
        subtypes,
        extra_paths,
        builtin_paths,
        generic,
    )

    # Any.
    if typ is Any:
        return True

    # Literal.
    if typing_inspect.is_literal_type(typ):
        return _check_literal(obj, typ, *args)

    # Union.
    if typing_inspect.is_union_type(typ):
        return _check_union(obj, typ, *args)

    # Type.
    if get_typing(get_origin(typ)) is Type:
        return _check_type(obj, typ, *args)

    # Tuple.
    if typing_inspect.is_tuple_type(typ):
        return _check_tuple(obj, typ, *args)

    # Mapping.
    try:
        type_is_mapping = issubclass(get_typing(get_origin(typ)), Mapping)
    except TypeError:
        pass
    else:
        if type_is_mapping:
            return _check_mapping(obj, typ, *args)

    # Iterable.
    try:
        type_is_iterable = issubclass(get_typing(get_origin(typ)), Iterable)
    except TypeError:
        pass
    else:
        if type_is_iterable:
            return _check_iterable(obj, typ, *args)

    # Forward reference.
    if isinstance(typ, ForwardRef):
        return _check_forward_ref(obj, typ, *args)

    # Not typing.
    return _check(obj, typ, args[0], args[1], False, *args[3:])


def _check(
    obj,
    typ,
    type_depth,
    instance,
    typing,
    subtypes,
    extra_paths,
    builtin_paths,
    generic,
):

    # Import lazy path.
    if isinstance(typ, six.string_types):
        typ = import_path(
            typ,
            extra_paths=extra_paths,
            builtin_paths=builtin_paths,
            generic=generic,
        )

    # Convert None to NoneType.
    if typ is None:
        typ = type(None)

    # Typing check.
    if typing:
        typing_name = get_name(typ)
        if typing_name is not None:
            return _check_typing(
                obj,
                typ,
                type_depth,
                instance,
                typing,
                subtypes,
                extra_paths,
                builtin_paths,
                generic,
            )

    # Invalid type.
    if not isinstance(typ, type) and not hasattr(typ, "__subclasscheck__"):
        error = "{!r} object is not a valid type".format(type(typ).__name__)
        raise TypeError(error)

    # Resolve type depth.
    for i in range(type_depth - 1 if instance else type_depth):
        typ = type(typ)

    # Everything is an instance and subclass of object.
    if typ is object:
        return True

    # Switch to a subclass comparison when type depth is greater than 0.
    if type_depth > 0:
        if not isinstance(obj, type):
            return False
        instance = False

    # Instance checks.
    if instance:
        if subtypes:
            return isinstance(obj, typ)
        else:
            return type(obj) is typ

    # Subclass checks.
    elif not isinstance(obj, type):
        error = "{!r} object is not a class".format(type(obj).__name__)
        raise TypeError(error)
    elif subtypes:
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
    elif isinstance(types, type) or isinstance(types, six.string_types) or get_name(types) is not None:
        return (types,)  # type: ignore
    elif isinstance(types, Iterable):  # type: ignore
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
        elif get_name(typ) is not None:
            type_names_.append(repr(typ))
        else:
            type_names_.append(type(typ).__name__)
    return tuple(type_names_)


def import_types(
    types,  # type: Type | str | None | Iterable[Type | str | None]
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=None,  # type: Iterable[str] | None
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

    return cast("tuple[Type, ...]", format_types(imported_types))


def is_instance(
    obj,  # type: Any
    types,  # type: Type | str | None | Iterable[Type | str | None]
    subtypes=True,  # type: bool
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=None,  # type: Iterable[str] | None
    generic=True,  # type: bool
    typing=True,  # type: bool
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
    :param typing: Whether to check against typing.
    :return: True if it is an instance.
    """
    imported_types = import_types(types, extra_paths=extra_paths, builtin_paths=builtin_paths, generic=generic)
    return any(
        _check(
            obj=obj,
            typ=t,
            type_depth=0,
            instance=True,
            typing=typing,
            subtypes=subtypes,
            extra_paths=extra_paths,
            builtin_paths=builtin_paths,
            generic=generic,
        )
        for t in imported_types
    )


def is_subclass(
    cls,  # type: Type
    types,  # type: Type | str | None | Iterable[Type | str | None]
    subtypes=True,  # type: bool
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=None,  # type: Iterable[str] | None
    generic=True,  # type: bool
    typing=True,  # type: bool
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
    :param typing: Whether to check against typing.
    :return: True if it is a subclass.
    :raises TypeError: Did not provide a class.
    """
    if not isinstance(cls, type):
        error = "is_subclass() arg 1 must be a class"
        raise TypeError(error)
    imported_types = import_types(types, extra_paths=extra_paths, builtin_paths=builtin_paths, generic=generic)
    return any(
        _check(
            obj=cls,
            typ=t,
            type_depth=0,
            instance=False,
            typing=typing,
            subtypes=subtypes,
            extra_paths=extra_paths,
            builtin_paths=builtin_paths,
            generic=generic,
        )
        for t in imported_types
    )


def is_iterable(value, include_strings=False):
    # type: (Any, bool) -> bool
    """
    Tell whether a value is an iterable or not.
    By default, strings are not considered iterables.

    :param value: Value.
    :param include_strings: Whether to consider strings as iterables.
    :return: True if iterable.
    """
    return isinstance(value, Iterable) and (  # type: ignore
        (not isinstance(value, six.string_types) or include_strings)
    )


def assert_is_instance(
    obj,  # type: _T
    types,  # type: Type[_T] | str | None | Iterable[Type[_T] | str | None]
    subtypes=True,  # type: bool
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=None,  # type: Iterable[str] | None
    generic=True,  # type: bool
    typing=True,  # type: bool
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
    :param typing: Whether to check against typing.
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
        typing=typing,
    ):
        types = format_types(types)
        if not types:
            error = "no types were provided to perform assertion"
            raise ValueError(error)
        error = "got {!r} object, expected instance of {}{}".format(
            type(obj).__name__,
            ", ".join(repr(n) for n in type_names(types)),
            "" if subtypes else " (instances of subclasses are not accepted)",
        )
        raise TypeCheckError(error)
    return obj


def assert_is_subclass(
    cls,  # type: Type[_T]
    types,  # type: Type[_T] | str | None | Iterable[Type[_T] | str | None]
    subtypes=True,  # type: bool
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=None,  # type: Iterable[str] | None
    generic=True,  # type: bool
    typing=True,  # type: bool
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
    :param typing: Whether to check against typing.
    :raises ValueError: No types were provided.
    :raises TypeCheckError: Class is not a subclass of provided types.
    """
    if not isinstance(cls, type):
        types = format_types(types)
        error = "got instance of {!r}, expected {}{}{}".format(
            type(cls).__name__,
            "one of " if len(types) > 1 else "class ",
            ", ".join(repr(n) for n in type_names(types)),
            "" if subtypes else " (subclasses are not accepted)",
        )
        raise TypeCheckError(error)

    if not is_subclass(
        cls,
        types,
        subtypes=subtypes,
        extra_paths=extra_paths,
        builtin_paths=builtin_paths,
        generic=generic,
        typing=typing,
    ):
        types = format_types(types)
        if not types:
            error = "no types were provided to perform assertion"
            raise ValueError(error)

        error = "got {!r}, expected {}{}{}".format(
            cls.__name__,
            "one of " if len(types) > 1 else "class ",
            ", ".join(repr(n) for n in type_names(types)),
            "" if subtypes else " (subclasses are not accepted)",
        )
        raise TypeCheckError(error)

    return cast(Type[_T], cls)


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
