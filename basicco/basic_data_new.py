from collections import OrderedDict
from enum import Enum

import six
from tippo import Any, Callable, NamedTuple, TypeVar, dataclass_transform, cast

from ._bases import SlottedBaseMeta, SlottedBase
from .get_mro import preview_mro
from .mangling import mangle, unmangle
from .dynamic_code import generate_unique_filename, make_function
from .custom_repr import mapping_repr
from .safe_repr import safe_repr
from .recursive_repr import recursive_repr

__all__ = ["field", "to_items", "to_dict", "BasicDataMeta", "BasicData"]


T = TypeVar("T")


class _MissingType(Enum):
    MISSING = "MISSING"


class _DefaultType(Enum):
    DEFAULT = "DEFAULT"


# Sentinel value for missing values.
_MISSING = _MissingType.MISSING

# Sentinel value for default values.
_DEFAULT = _DefaultType.DEFAULT


# Global field count for ordering.
_field_count = 0


# Field type.
_Field = NamedTuple(
    "_Field",
    (
        ("id", int),
        ("default", Any),
        ("factory", Any),
        ("init", bool),
        ("repr", bool),
        ("eq", bool),
        ("hash", bool),
        ("frozen", bool),
    ),
)


def field(
    default=_MISSING,  # type: T | _MissingType
    factory=_MISSING,  # type: Callable[..., T] | _MissingType
    init=True,  # type: bool
    repr=True,  # type: bool
    eq=True,  # type: bool
    hash=None,  # type: bool | None
    frozen=True,  # type: bool
):
    # type: (...) -> T
    """
    Define a data field.

    :param default: Default value.
    :param factory: Default factory.
    :param init: Whether to include in `__init__`.
    :param repr: Whether to include in `__repr__`.
    :param eq: Whether to include in `__eq__`.
    :param hash: Whether to include in `__hash__`.
    :param frozen: Whether should be frozen.
    """
    global _field_count

    # Increment field count.
    _field_count += 1
    id_ = _field_count

    # Ensure single default source.
    if default is not _MISSING and factory is not _MISSING:
        error = "can't declare both 'default' and 'factory'"
        raise ValueError(error)

    # Ensure safe hash.
    eq = bool(eq)
    if hash is None:
        hash = eq
    hash = bool(hash)
    if hash and not eq:
        error = "can't contribute to the hash when not contributing to the eq"
        raise ValueError(error)

    # Other parameters.
    init = bool(init)
    repr = bool(repr)
    frozen = bool(frozen)

    _field = _Field(  # noqa
        id=id_,
        default=default,
        factory=factory,
        init=init,
        repr=repr,
        eq=eq,
        hash=hash,
        frozen=frozen,
    )
    return cast(T, _field)


# TODO: def cls_fields(cls)
# TODO: def replace(__data, **replaces)
# TODO: def delete(__data, *deletes)


def to_items(__data):
    # type: (BasicData) -> list[tuple[str, Any]]
    """
    Convert data to ordered items.

    :param __data: Data.
    :return: Items.
    """
    items = []
    for field_name, field_ in type(__data).__fields__.items():
        value = getattr(__data, field_name, _MISSING)
        if value is not _MISSING:
            items.append((field_name, value))
    return items


def to_dict(__data):
    # type: (BasicData) -> dict[str, Any]
    """
    Convert data to dictionary.

    :param __data: Data.
    :return: Dictionary.
    """
    return dict(to_items(__data))


def _has_default(field_):
    # type: (_Field) -> bool
    """
    Get whether field has default value.

    :param field_: Field.
    :return: True if has default value.
    """
    return field_.default is not _MISSING


def _has_factory(field_):
    # type: (_Field) -> bool
    """
    Get whether field has default factory.

    :param field_: Field.
    :return: True if has default factory.
    """
    return field_.factory is not _MISSING


def _has_any_default(field_):
    # type: (_Field) -> bool
    """
    Get whether field has default value (or factory).

    :param field_: Field.
    :return: True if has default.
    """
    return _has_default(field_) or _has_factory(field_)


def _make_init(module, cls_fields, cls_name, kw_only):
    # type: (str, OrderedDict[str, _Field], str, bool) -> Callable[..., None]
    """
    Make `__init__` method function.

    :param module: Module.
    :param cls_fields: Ordered dictionary of named cls_fields.
    :param kw_only: Whether to accept keyword arguments only.
    :param cls_name: Class name.
    :return: Method function.
    """
    script = "def __init__(self"
    globs = {"object": object}  # type: dict[str, Any]
    params = []  # type: list[str]
    lines = []  # type: list[str]
    seen_default = None  # type: str | None
    for field_name, field_ in cls_fields.items():
        if not field_.init:
            continue

        # Non-default field.
        if not _has_any_default(field_):

            # Not forcing keyword arguments.
            if not kw_only:

                # Non-default field after default field, error out.
                if seen_default is not None:
                    error = "non-default field {!r} declared after default field {!r}".format(field_name, seen_default)
                    raise TypeError(error)

                # Simple argument.
                params.append(field_name)
                lines.append("object.__setattr__(self, '{f}', {f})".format(f=field_name))

            # Forcing keyword arguments.
            else:
                globs["_MISSING"] = _MISSING
                params.append("{f}=_MISSING".format(f=field_name))
                lines.append("if {f} is _MISSING:".format(f=field_name))
                lines.append("    error = 'missing value for required keyword argument {f}'".format(f=field_name))
                lines.append("    raise TypeError(error)")
                lines.append("object.__setattr__(self, '{f}', {f})".format(f=field_name))

        # Default field.
        else:

            # Default variable name.
            default_var = "DEFAULT_{f}".format(f=field_name.upper())
            while default_var in cls_fields:
                default_var = "{}_".format(default_var)

            # Field has a default value.
            if _has_default(field_):
                globs[default_var] = field_.default
                params.append("{}={}".format(field_name, default_var))
                lines.append("object.__setattr__(self, '{f}', {f})".format(f=field_name))

            # Field has a factory.
            else:
                assert _has_factory(field_)
                globs[default_var] = _DEFAULT
                params.append("{}={}".format(field_name, default_var))
                lines.append(
                    "object.__setattr__(self, '{f}', type(self).__fields__['{f}'].factory())".format(f=field_name)
                )

    script += (", " + ", ".join(params) if params else "") + "):\n"
    script += ("    " + "\n    ".join(lines) + "\n") if lines else ""
    script += "    if hasattr(self, '__post_init__'):\n"
    script += "        self.__post_init__()\n"

    return make_function(
        "__init__",
        script,
        globs,
        generate_unique_filename("__init__", module, cls_name),
        module,
    )


def _make_eq(module, cls_fields, cls_name):
    # type: (str, OrderedDict[str, _Field], str) -> Callable[..., None]
    """
    Make `__eq__` method function.

    :param module: Module.
    :param cls_fields: Ordered dictionary of named cls_fields.
    :param cls_name: Class name.
    :return: Method function.
    """
    script = "def __eq__(self, other):\n"
    script += "    if self is other:\n"
    script += "        return True\n"
    script += "    if type(self) is not type(other):\n"
    script += "        return False"
    globs = {"_MISSING": _MISSING}  # type: dict[str, Any]
    lines = []  # type: list[str]
    for field_name, field_ in cls_fields.items():
        if not field_.eq:
            continue
        assert field_.hash
        lines.append("if getattr(self, '{f}', _MISSING) != getattr(other, '{f}', _MISSING):".format(f=field_name))
        lines.append("    return False")

    script += ("\n    " + "\n    ".join(lines)) if lines else ""
    script += "\n    return True\n"

    return make_function(
        "__eq__",
        script,
        globs,
        generate_unique_filename("__eq__", module, cls_name),
        module,
    )


def _make_repr(module, cls_fields, cls_name):  # noqa
    # type: (str, OrderedDict[str, _Field], str) -> Callable[..., None]
    """
    Make `__repr__` method function.

    :param module: Module.
    :param cls_fields: Ordered dictionary of named cls_fields.
    :param cls_name: Class name.
    :return: Method function.
    """
    script = "@safe_repr\n"
    script += "@recursive_repr\n"
    script += "def __repr__(self):\n"
    script += "    return mapping_repr(\n"
    script += "        to_items(self),\n"
    script += "        prefix='" + cls_name + "(',\n"
    script += "        suffix=')',\n"
    script += "        template='{key}={value}',\n"
    script += "        key_repr=str\n"
    script += "    )\n"
    globs = {
        "safe_repr": safe_repr,
        "recursive_repr": recursive_repr,
        "mapping_repr": mapping_repr,
        "to_items": to_items,
        "str": str,
    }  # type: dict[str, Any]
    print(script)

    return make_function(
        "__repr__",
        script,
        globs,
        generate_unique_filename("__repr__", module, cls_name),
        module,
    )


def _make_hash(module, cls_fields, cls_name):
    # type: (str, OrderedDict[str, _Field], str) -> Callable[..., None] | None
    """
    Make `__hash__` method function (or None for mutable classes).

    :param module: Module.
    :param cls_fields: Ordered dictionary of named cls_fields.
    :param cls_name: Class name.
    :return: Method function or None.
    """
    script = "def __hash__(self):\n"
    script += "    return hash(("
    globs = {"_MISSING": _MISSING}  # type: dict[str, Any]
    lines = []  # type: list[str]
    for field_name, field_ in cls_fields.items():
        if not field_.hash:
            continue
        if not field_.frozen:
            return None
        lines.append("getattr(self, '{f}', _MISSING)".format(f=field_name))

    script += ("\n        " + ",\n        ".join(lines) + "\n") if lines else ""
    script += "    ))\n"

    return make_function(
        "__hash__",
        script,
        globs,
        generate_unique_filename("__eq__", module, cls_name),
        module,
    )


@dataclass_transform(field_specifiers=(field,))
class BasicDataMeta(SlottedBaseMeta):
    """Metaclass for :class:`BasicData`."""

    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):  # noqa
        # type: (...) -> BasicDataMeta
        dct = dict(dct)

        # Gather cls_fields for this class.
        __fields = dct[mangle("__fields", name)] = dict((n, f) for n, f in dct.items() if isinstance(f, _Field))

        # Convert them to slots.
        dct["__slots__"] = tuple(
            sorted(set(dct.get("__slots__", ())).union(unmangle(n, name) for n in __fields if dct.pop(n)))
        )

        # Loop through mro.
        mro = [
            (b.__name__, b.__dict__, b.__dict__.get(mangle("__fields", b.__name__), {}), isinstance(b, BasicDataMeta))
            for b in preview_mro(*bases)
        ] + [(name, dct, __fields, True)]
        all_fields = {}
        field_ids = {}
        for base_name, base_dct, base_fields, is_data in mro:

            # Prevent bad overrides.
            for member_name, member in base_dct.items():
                if isinstance(member, _Field):
                    assert not is_data
                    error = "non-data class {!r} defines a {!r} field".format(base_name, member_name)
                    raise TypeError(error)
                if member_name not in base_fields and member_name in all_fields:
                    error = "class {!r} overrides field {!r} with non-field {!r} object".format(
                        base_name, member_name, type(member).__name__
                    )
                    raise TypeError(error)

            # Keep track of cls_fields.
            for field_name, field_ in base_fields.items():
                if field_name in ("object", "_MISSING", "_DEFAULT"):
                    error = "invalid field name {!r}".format(field_name)
                    raise ValueError(error)
                all_fields[field_name] = field_
                if field_name not in field_ids:
                    field_ids[field_name] = field_.id

        # Order cls_fields by id and store them in a ordered dict.
        __fields__ = dct["__fields__"] = OrderedDict(sorted(all_fields.items(), key=lambda i: field_ids[i[0]]))

        # Build class and return it.
        try:
            return super(BasicDataMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
        except TypeError as e:
            exc = TypeError(e)
            six.raise_from(exc, None)
            raise exc


class BasicData(six.with_metaclass(BasicDataMeta, SlottedBase)):
    """Basic data class."""

    __slots__ = ()
    __fields__ = OrderedDict()  # type: OrderedDict[str, _Field]
    __params__ = {}  # type: dict[str, bool]

    def __init_subclass__(
        cls,
        kw_only=None,  # type: bool | None
        init=None,  # type: bool | None
        repr=None,  # type: bool | None
        eq=None,  # type: bool | None
        hash=None,  # type: bool | None
        unsafe_hash=False,  # type: bool
    ):
        # type: (...) -> None
        """
        Initialize subclass with parameters.

        :param kw_only: Force keyword-only arguments in generated `__init__` method.
        :param init: Whether to generate `__init__` method.
        :param repr: Whether to generate `__repr__` method.
        :param eq: Whether to generate `__eq__` method.
        :param hash: Whether to generate `__hash__` method.
        :param unsafe_hash: Whether to allow manual declaration of potentially unsafe `__hash__` method.
        """

        # Merge parameters.
        type.__setattr__(
            cls,
            "__params__",
            dict(
                cls.__params__,
                **dict(
                    (n, bool(v))
                    for n, v in {"kw_only": kw_only, "init": init, "repr": repr, "eq": eq, "hash": hash}.items()
                    if v is not None
                )
            ),
        )

        # __init__
        if cls.__params__.get("init", True):
            if "__init__" in cls.__dict__:
                error = "auto generated '__init__' method can't be overriden without disabling 'init' parameter"
                raise TypeError(error)
            type.__setattr__(
                cls,
                "__init__",
                _make_init(cls.__module__, cls.__fields__, cls.__name__, cls.__params__.get("kw_only", False)),
            )
        elif "__init__" not in cls.__dict__:
            type.__setattr__(cls, "__init__", object.__init__)

        # __repr__
        if cls.__params__.get("repr", True):
            if "__repr__" in cls.__dict__:
                error = "auto generated '__repr__' method can't be overriden without disabling 'repr' parameter"
                raise TypeError(error)
            type.__setattr__(
                cls,
                "__repr__",
                _make_repr(cls.__module__, cls.__fields__, cls.__name__),
            )
        elif "__repr__" not in cls.__dict__:
            type.__setattr__(cls, "__repr__", object.__init__)

        # __eq__
        if cls.__params__.get("eq", True):
            if "__eq__" in cls.__dict__:
                error = "auto generated '__eq__' method can't be overriden without disabling 'eq' parameter"
                raise TypeError(error)
            type.__setattr__(cls, "__eq__", _make_eq(cls.__module__, cls.__fields__, cls.__name__))
        elif "__eq__" not in cls.__dict__ and "__hash__" not in cls.__dict__:
            type.__setattr__(cls, "__eq__", object.__eq__)

        # __hash__
        if cls.__params__.get("hash", True):
            if "__hash__" in cls.__dict__:
                error = (
                    "auto generated '__hash__' method can't be overriden without disabling parameters 'hash' & 'eq' "
                    "and enabling 'unsafe_hash'"
                )
                raise TypeError(error)
            type.__setattr__(cls, "__hash__", _make_hash(cls.__module__, cls.__fields__, cls.__name__))
        elif "__hash__" not in cls.__dict__:
            if cls.__eq__ is object.__eq__:
                type.__setattr__(cls, "__hash__", object.__hash__)
            else:
                type.__setattr__(cls, "__hash__", None)
        elif not unsafe_hash:
            error = "it's unsafe to declare your own '__hash__' method"
            raise TypeError(error)
        elif cls.__params__.get("eq", True):
            error = "can't declare your own '__hash__' method without disabling the 'eq' parameter"
            raise TypeError(error)
        elif "__eq__" not in cls.__dict__:
            error = "when declaring your own '__hash__' method you also need to declare '__eq__'"
            raise TypeError(error)

        # __setattr__
        # TODO

        # __delattr__
        # TODO
