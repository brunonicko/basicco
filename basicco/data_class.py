"""Python 2.7 compatible implementation of slotted data classes based on a metaclass."""

import copy
from collections import OrderedDict
from enum import Enum

import six
from tippo import Any, Callable, Final, Literal, Type, TypedDict, TypeVar, cast, dataclass_transform

from ._bases import SlottedBase, SlottedBaseMeta
from .custom_repr import mapping_repr
from .dynamic_code import generate_unique_filename, make_function
from .get_mro import preview_mro
from .mangling import mangle, unmangle
from .mapping_proxy import MappingProxyType
from .recursive_repr import recursive_repr
from .runtime_final import final
from .safe_repr import safe_repr

__all__ = ["field", "fields", "replace", "deletes", "as_items", "as_dict", "as_tuple", "DataClassMeta", "DataClass"]


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


@final
class _Field(SlottedBase):
    """Field type."""

    __slots__ = (
        "id",
        "property",
        "default",
        "default_factory",
        "converter",
        "init",
        "kw_only",
        "repr",
        "eq",
        "hash",
        "frozen",
        "order",
        "required",
    )

    def __init__(
        self,
        default,  # type: T | _MissingType
        default_factory,  # type: Callable[..., T] | _MissingType
        converter,  # type: Callable[[Any], T] | None
        init,  # type: bool
        kw_only,  # type: bool
        repr,  # type: bool
        eq,  # type: bool
        hash,  # type: bool | None
        frozen,  # type: bool
        order,  # type: bool | None
        required,  # type: bool | None
    ):
        # type: (...) -> None

        # Ensure single default source.
        if default is not _MISSING and default_factory is not _MISSING:
            error = "can't declare both 'default' and 'default_factory'"
            raise ValueError(error)

        # Ensure safe hash.
        eq = bool(eq)
        if hash is None:
            hash = eq
        hash = bool(hash)
        if hash and not eq:
            error = "can't contribute to the hash when not contributing to the eq"
            raise ValueError(error)

        # Ensure safe required and order.
        if order is None:
            if required is None:
                required = True
            order = eq and required
        else:
            order = bool(order)
        if order and required is None:
            required = True
        else:
            required = bool(required)
        if order and not eq:
            error = "can't contribute to order if it's not contributing to the eq"
            raise ValueError(error)
        if order and not required:
            error = "can't contribute to order if it's not required"
            raise ValueError(error)

        # Cast parameters.
        init = bool(init)
        kw_only = bool(kw_only)
        repr = bool(repr)
        frozen = bool(frozen)

        # Increment field count.
        global _field_count
        _field_count += 1

        self.default = default  # type: T | _MissingType
        self.default_factory = default_factory  # type: Callable[..., T] | _MissingType
        self.converter = converter  # type: Callable[[Any], T] | None
        self.init = init  # type: bool
        self.kw_only = kw_only  # type: bool
        self.repr = repr  # type: bool
        self.eq = eq  # type: bool
        self.hash = hash  # type: bool
        self.frozen = frozen  # type: bool
        self.order = order  # type: bool
        self.required = required  # type: bool
        self.id = _field_count  # type: int
        self.property = None  # type: property | None

    def __call__(self, fget):
        # type: (T) -> T
        """
        Allows field to be used as a decorator for a property's getter function.

        :param fget: Getter method function.
        :return: Decorated getter method function.
        """
        object.__setattr__(fget, "__field__", self)
        return fget

    def __hash__(self):
        return hash(tuple(self.__items()))

    def __eq__(self, other):
        return type(self) is type(other) and self.__items() == other.__items()

    def __setattr__(self, name, value):
        if hasattr(self, name) and not name.startswith("_"):
            error = "can't set read-only attribute {!r}".format(name)
            raise AttributeError(error)
        super(_Field, self).__setattr__(name, value)

    def __delattr__(self, name):
        if hasattr(self, name) and not name.startswith("_"):
            error = "can't delete read-only attribute {!r}".format(name)
            raise AttributeError(error)
        super(_Field, self).__delattr__(name)

    @safe_repr
    @recursive_repr
    def __repr__(self):
        # type: () -> str
        return mapping_repr(
            self.__items(),
            template="{key}={value}",
            prefix="Field(",
            suffix=")",
            key_repr=str,
            value_repr=repr,
        )

    def __items(self):
        return [
            ("default", self.default),
            ("default_factory", self.default_factory),
            ("converter", self.converter),
            ("init", self.init),
            ("kw_only", self.kw_only),
            ("repr", self.repr),
            ("eq", self.eq),
            ("hash", self.hash),
            ("frozen", self.frozen),
            ("order", self.order),
            ("id", self.id),
            ("property", self.property),
        ]


def field(
    default=_MISSING,  # type: T | _MissingType
    default_factory=_MISSING,  # type: Callable[..., T] | _MissingType
    converter=None,  # type: Callable[[Any], T] | None
    init=True,  # type: bool
    kw_only=False,  # type: bool
    repr=True,  # type: bool
    eq=True,  # type: bool
    hash=None,  # type: bool | None
    frozen=False,  # type: bool
    order=None,  # type: bool | None
    required=None,  # type: bool | None
):
    # type: (...) -> T
    """
    Define a field.

    :param default: Default value.
    :param default_factory: Default value factory.
    :param converter: Value converter.
    :param init: Whether to include in `__init__`.
    :param kw_only: Whether to only accept keyword argument initialization.
    :param repr: Whether to include in `__repr__`.
    :param eq: Whether to include in `__eq__`.
    :param hash: Whether to include in `__hash__`.
    :param frozen: Whether should be frozen (immutable).
    :param order: Whether to include in order methods.
    :param required: Whether to require a value after initialization/replacement.
    """
    _field = _Field(
        default=default,
        default_factory=default_factory,
        converter=converter,
        init=init,
        kw_only=kw_only,
        repr=repr,
        eq=eq,
        hash=hash,
        frozen=frozen,
        order=order,
        required=required,
    )
    return cast(T, _field)


def fields(cls):
    # type: (Type[DataClass]) -> OrderedDict[str, _Field]
    """
    Get data class fields.

    :param cls: Data class.
    :return: Ordered dictionary of fields.
    """
    return OrderedDict(cls.__fields__)


def replace(__data, **replacements):
    # type: (DataClass, **Any) -> DataClass
    """
    Make a copy with replaced field values.

    :param __data: Data.
    :param replacements: Field value replacements.
    :return: Data with replacements.
    """
    new_data = copy.copy(__data)
    for name, value in replacements.items():
        converter = type(__data).__fields__[name].converter
        if converter is not None:
            value = converter(value)
        object.__setattr__(new_data, name, value)
    return new_data


def deletes(__data, *deletions):
    # type: (DataClass, *str) -> DataClass
    """
    Make a copy with deleted field values.

    :param __data: Data.
    :param deletions: Fields to delete.
    :return: Data with deletions.
    """
    cls = type(__data)
    required = set(n for n, f in cls.__fields__.items() if f.required).intersection(deletions)
    if required:
        error = "can't delete required field(s) {}".format(", ".join(repr(r) for r in required))
        raise AttributeError(error)
    new_data = copy.copy(__data)
    for name in deletions:
        object.__delattr__(new_data, name)
    return new_data


def _as_items(converter, data, recursively):
    # type: (Callable[..., Any], DataClass, bool) -> list[tuple[str, Any]]
    items = []
    for field_name, field_ in type(data).__fields__.items():
        value = getattr(data, field_name, _MISSING)
        if value is _MISSING:
            continue
        if recursively:
            if isinstance(value, DataClass):
                value = converter(value, True)
            elif isinstance(value, (tuple, list, set, frozenset)):
                value = type(value)(converter(v, True) if isinstance(v, DataClass) else v for v in value)
            elif isinstance(value, (dict, MappingProxyType)):
                value = type(value)(
                    dict((k, converter(v, True)) if isinstance(v, DataClass) else (k, v) for k, v in value.items())
                )
        items.append((field_name, value))
    return items


def as_items(data, recursively=True):
    # type: (DataClass, bool) -> list[tuple[str, Any]]
    """
    Convert data to ordered items.

    :param data: Data.
    :param recursively: Whether to convert recursively.
    :return: Items.
    """
    return _as_items(as_items, data, recursively)


def as_dict(data, recursively=True):
    # type: (DataClass, bool) -> dict[str, Any]
    """
    Convert data to dictionary.

    :param data: Data.
    :param recursively: Whether to convert recursively.
    :return: Dictionary.
    """
    return dict(_as_items(as_dict, data, recursively))


def as_tuple(data, recursively=True):
    # type: (DataClass, bool) -> tuple[Any, ...]
    """
    Convert data to a tuple.

    :param data: Data.
    :param recursively: Whether to convert recursively.
    :return: Tuple.
    """
    return tuple(list(zip(*_as_items(as_tuple, data, recursively)))[1])


def _has_default(field_):
    # type: (_Field) -> bool
    """
    Get whether field has default value.

    :param field_: Field.
    :return: True if has default value.
    """
    return field_.default is not _MISSING


def _has_default_factory(field_):
    # type: (_Field) -> bool
    """
    Get whether field has default default_factory.

    :param field_: Field.
    :return: True if has default default_factory.
    """
    return field_.default_factory is not _MISSING


def _has_any_default(field_):
    # type: (_Field) -> bool
    """
    Get whether field has default value (or default_factory).

    :param field_: Field.
    :return: True if has default.
    """
    return _has_default(field_) or _has_default_factory(field_)


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
    required_lines = []  # type: list[str]
    seen_default = None  # type: str | None
    for field_name, field_ in cls_fields.items():

        # Add required field check.
        if field_.required and not field_.init:
            required_lines.append("if not hasattr(self, '{f}'):".format(f=field_name))
            required_lines.append("    error = 'missing value for required attribute {f}'".format(f=field_name))
            required_lines.append("    raise TypeError(error)")

        # Skip non-init fields.
        if not field_.init:
            continue

        # Converter variable name.
        converter_var = "{f}_converter".format(f=field_name)
        while converter_var in cls_fields:
            converter_var = "{}_".format(converter_var)
        if field_.converter is not None:
            globs[converter_var] = field_.converter

        # Non-default field.
        if not _has_any_default(field_):

            # Not forcing keyword arguments.
            if not kw_only and not field_.kw_only:

                # Non-default field after default field, error out.
                if seen_default is not None:
                    error = "non-default field {!r} declared after default field {!r}".format(field_name, seen_default)
                    raise TypeError(error)

                # Simple argument.
                params.append(field_name)
                if field_.converter is None:
                    lines.append("object.__setattr__(self, '{f}', {f})".format(f=field_name))
                else:
                    lines.append("object.__setattr__(self, '{f}', {c}({f}))".format(c=converter_var, f=field_name))

            # Forcing keyword arguments.
            else:
                seen_default = field_name
                globs["_MISSING"] = _MISSING
                params.append("{f}=_MISSING".format(f=field_name))
                lines.append("if {f} is _MISSING:".format(f=field_name))
                lines.append("    error = 'missing value for required keyword argument {f}'".format(f=field_name))
                lines.append("    raise TypeError(error)")
                if field_.converter is None:
                    lines.append("object.__setattr__(self, '{f}', {f})".format(f=field_name))
                else:
                    lines.append("object.__setattr__(self, '{f}', {c}({f}))".format(c=converter_var, f=field_name))

        # Default field.
        else:
            seen_default = field_name

            # Default variable name.
            default_var = "DEFAULT_{f}".format(f=field_name.upper())
            while default_var in cls_fields:
                default_var = "{}_".format(default_var)

            # Field has a default value.
            if _has_default(field_):
                globs[default_var] = field_.default
                params.append("{}={}".format(field_name, default_var))
                if field_.converter is None:
                    lines.append("object.__setattr__(self, '{f}', {f})".format(f=field_name))
                else:
                    lines.append("object.__setattr__(self, '{f}', {c}({f}))".format(c=converter_var, f=field_name))

            # Field has a default factory.
            else:
                assert _has_default_factory(field_)
                globs[default_var] = _DEFAULT
                params.append("{}={}".format(field_name, default_var))
                lines.append("if {} is {}:".format(field_name, default_var))
                if field_.converter is None or field_.converter is field_.default_factory:
                    lines.append(
                        "    object.__setattr__(self, '{f}', type(self).__fields__['{f}'].default_factory())".format(
                            f=field_name
                        )
                    )
                else:
                    lines.append(
                        "    object.__setattr__(self, '{f}', "
                        "{c}(type(self).__fields__['{f}'].default_factory()))".format(c=converter_var, f=field_name)
                    )
                lines.append("else:")
                if field_.converter is None:
                    lines.append("    object.__setattr__(self, '{f}', {f})".format(f=field_name))
                else:
                    lines.append("    object.__setattr__(self, '{f}', {c}({f}))".format(c=converter_var, f=field_name))

    script += (", " + ", ".join(params) if params else "") + "):\n"
    script += ("    " + "\n    ".join(lines) + "\n") if lines else ""
    script += "    if hasattr(self, '__post_init__'):\n"
    script += "        self.__post_init__()\n"
    script += ("    " + "\n    ".join(required_lines) + "\n") if lines else ""

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


def _make_repr(module, cls_fields, cls_name, kw_only):  # noqa
    # type: (str, OrderedDict[str, _Field], str, bool) -> Callable[..., None]
    """
    Make `__repr__` method function.

    :param module: Module.
    :param cls_fields: Ordered dictionary of named cls_fields.
    :param cls_name: Class name.
    :param kw_only: Whether to accept keyword arguments only.
    :return: Method function.
    """
    script = "@safe_repr\n"
    script += "@recursive_repr\n"
    script += "def __repr__(self):\n"
    script += "    repr_str = '{}('\n".format(cls_name)
    script += "    parts = []\n"
    for field_name, field_ in cls_fields.items():
        script += "    if hasattr(self, '{f}'):\n".format(f=field_name)
        if kw_only or _has_any_default(field_) or field_.kw_only:
            script += "        parts.append('" + field_name + "={!r}'.format(getattr(self, '" + field_name + "')))\n"
        else:
            script += "        parts.append('{!r}'.format(getattr(self, '" + field_name + "')))\n"
    script += "    repr_str += ', '.join(parts) + ')'\n"
    script += "    return repr_str\n"
    globs = {"safe_repr": safe_repr, "recursive_repr": recursive_repr, "type": type}  # type: dict[str, Any]

    return make_function(
        "__repr__",
        script,
        globs,
        generate_unique_filename("__repr__", module, cls_name),
        module,
    )


def _make_hash(module, cls_fields, cls_name, frozen_cls):
    # type: (str, OrderedDict[str, _Field], str, bool) -> Callable[..., None] | None
    """
    Make `__hash__` method function (or None for mutable classes).

    :param module: Module.
    :param cls_fields: Ordered dictionary of named cls_fields.
    :param cls_name: Class name.
    :param frozen_cls: Whether class is frozen.
    :return: Method function or None.
    """
    script = "def __hash__(self):\n"
    script += "    return hash(("
    globs = {"_MISSING": _MISSING}  # type: dict[str, Any]
    lines = []  # type: list[str]
    for field_name, field_ in cls_fields.items():
        if not field_.hash:
            continue
        if not frozen_cls and not field_.frozen:
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


def _make_setattr(module, cls_fields, cls_name, frozen_cls):
    # type: (str, OrderedDict[str, _Field], str, bool) -> Callable[..., None]
    """
    Make `__setattr__` method function.

    :param module: Module.
    :param cls_fields: Ordered dictionary of named cls_fields.
    :param cls_name: Class name.
    :param frozen_cls: Whether class is frozen.
    :return: Method function.
    """
    script = "def __setattr__(self, name, value):\n"
    globs = {"object": object, "type": type}  # type: dict[str, Any]
    lines = []  # type: list[str]
    if frozen_cls:
        lines.append("error = 'class {} is frozen'".format(cls_name))
        lines.append("raise AttributeError(error)")
    else:
        if any(f.frozen for f in cls_fields.values()):
            lines.append("if name in {!r}:".format(set(n for n, f in cls_fields.items() if f.frozen)))
            lines.append("    error = 'field {!r} is frozen'.format(name)")
            lines.append("    raise AttributeError(error)")
        if any(f.converter is not None for f in cls_fields.values()):
            lines.append("if name in {!r}:".format(set(n for n, f in cls_fields.items() if f.converter is not None)))
            lines.append("    value = type(self).__fields__[name].converter(value)")
        lines.append("object.__setattr__(self, name, value)")

    script += (("    " + "\n    ".join(lines)) if lines else "") + "\n"

    return make_function(
        "__setattr__",
        script,
        globs,
        generate_unique_filename("__setattr__", module, cls_name),
        module,
    )


def _make_delattr(module, cls_fields, cls_name, frozen_cls):
    # type: (str, OrderedDict[str, _Field], str, bool) -> Callable[..., None]
    """
    Make `__delattr__` method function.

    :param module: Module.
    :param cls_fields: Ordered dictionary of named cls_fields.
    :param cls_name: Class name.
    :param frozen_cls: Whether class is frozen.
    :return: Method function.
    """
    script = "def __delattr__(self, name):\n"
    globs = {"object": object}  # type: dict[str, Any]
    lines = []  # type: list[str]
    if frozen_cls:
        lines.append("error = 'class {} is frozen'".format(cls_name))
        lines.append("raise AttributeError(error)")
    else:
        lines.append("if name in {!r}:".format(set(n for n, f in cls_fields.items() if f.frozen)))
        lines.append("    error = 'field {!r} is frozen'.format(name)")
        lines.append("    raise AttributeError(error)")
        lines.append("object.__delattr__(self, name)")

    script += (("    " + "\n    ".join(lines)) if lines else "") + "\n"

    return make_function(
        "__delattr__",
        script,
        globs,
        generate_unique_filename("__delattr__", module, cls_name),
        module,
    )


_order_operators = {
    "__lt__": "<",
    "__le__": "<=",
    "__gt__": ">",
    "__ge__": ">=",
}


def _make_order(
    module,  # type: str
    cls_fields,  # type: OrderedDict[str, _Field]
    cls_name,  # type: str
    method_name,  # type: Literal["__lt__", "__le__", "__gt__", "__ge__"]
):
    # type: (...) -> Callable[..., None]
    """
    Make order method function.

    :param module: Module.
    :param cls_fields: Ordered dictionary of named cls_fields.
    :param cls_name: Class name.
    :param method_name: Method name.
    :return: Method function.
    """
    script = "def {}(self, other):\n".format(method_name)
    script += "    cls = type(self)\n"
    script += "    if cls is not type(other):\n"
    script += "        return NotImplemented\n"
    globs = {"object": object}  # type: dict[str, Any]
    self_parts = []  # type: list[str]
    other_parts = []  # type: list[str]
    for field_name, field_ in cls_fields.items():
        if not field_.order:
            continue

        self_parts.append("self.{f}".format(f=field_name))
        other_parts.append("other.{f}".format(f=field_name))

    script += "    self_values = (" + ", ".join(self_parts) + ")\n"
    script += "    other_values = (" + ", ".join(other_parts) + ")\n"
    script += "    return self_values {} other_values\n".format(_order_operators[method_name])

    return make_function(
        method_name,
        script,
        globs,
        generate_unique_filename(method_name, module, cls_name),
        module,
    )


def _make_match_args(cls_fields):
    # type: (OrderedDict[str, _Field]) -> tuple[str, ...]
    """
    Make `__match_args__` tuple class variable.

    :param cls_fields: Ordered dictionary of named cls_fields.
    :return: Match args tuple.
    """
    match_args = []
    for field_name, field_ in cls_fields.items():
        if not field_.init:
            continue
        match_args.append(field_name)
    return tuple(match_args)


DataClassParams = TypedDict(
    "DataClassParams",
    {
        "kw_only": bool,
        "init": bool,
        "repr": bool,
        "eq": bool,
        "hash": bool,
        "frozen": bool,
        "unsafe_hash": bool,
        "order": bool,
        "match_args": bool,
    },
    total=False,
)


@dataclass_transform(field_specifiers=(field,))
class DataClassMeta(SlottedBaseMeta):
    """Metaclass for :class:`DataClass`."""

    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):  # noqa
        # type: (...) -> DataClassMeta
        dct = dict(dct)

        # Gather fields for this class.
        __fields = dct[mangle("__fields", name)] = OrderedDict()
        for member_name, member in list(dct.items()):

            # Regular field.
            if isinstance(member, _Field):
                __fields[member_name] = member

            # Property field.
            elif isinstance(member, property) and member.fget is not None:
                if hasattr(member.fget, "__field__"):
                    field_ = member.fget.__field__
                    object.__delattr__(member.fget, "__field__")
                elif isinstance(member.fget, _Field):
                    field_ = member.fget
                    assert field_.default is not _MISSING  # noqa
                    dct[member_name] = member.getter(field_.default)  # noqa
                else:
                    continue
                object.__setattr__(field_, "property", member)
                object.__setattr__(field_, "init", member.fset is not None and field_.init)
                object.__setattr__(field_, "frozen", (member.fset is None and member.fdel is None) or field_.frozen)
                __fields[member_name] = field_

        # Convert non-property fields to slots.
        dct["__slots__"] = tuple(
            sorted(
                set(dct.get("__slots__", ())).union(
                    unmangle(n, name) for n, f in __fields.items() if f.property is None and dct.pop(n)
                )
            )
        )

        # Loop through mro.
        mro = [
            (b.__name__, b.__dict__, b.__dict__.get(mangle("__fields", b.__name__), {}), isinstance(b, DataClassMeta))
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

            # Keep track of fields.
            for field_name, field_ in base_fields.items():
                if field_name in ("object", "_MISSING", "_DEFAULT"):
                    error = "invalid field name {!r}".format(field_name)
                    raise ValueError(error)
                all_fields[field_name] = field_
                if field_name not in field_ids:
                    field_ids[field_name] = field_.id

        # Order fields by id and store them in a ordered dict.
        dct["__fields__"] = OrderedDict(sorted(all_fields.items(), key=lambda i: field_ids[i[0]]))

        # Build class and return it.
        try:
            return super(DataClassMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
        except TypeError as e:
            exc = TypeError(e)
            six.raise_from(exc, None)
            raise exc


class DataClass(six.with_metaclass(DataClassMeta, SlottedBase)):
    """Basic data class."""

    __slots__ = ()
    __fields__ = OrderedDict()  # type: Final[OrderedDict[str, _Field]]
    __params__ = {}  # type: Final[DataClassParams]
    __kwargs__ = {}  # type: DataClassParams

    def __init_subclass__(
        cls,
        kw_only=None,  # type: bool | None
        init=None,  # type: bool | None
        repr=None,  # type: bool | None
        eq=None,  # type: bool | None
        hash=None,  # type: bool | None
        frozen=None,  # type: bool | None
        unsafe_hash=False,  # type: bool
        order=None,  # type: bool | None
        match_args=None,  # type: bool | None
    ):
        # type: (...) -> None
        """
        Initialize subclass with parameters.

        :param kw_only: Force keyword-only arguments in generated `__init__` method.
        :param init: Whether to generate `__init__` method.
        :param repr: Whether to generate `__repr__` method.
        :param eq: Whether to generate `__eq__` method.
        :param hash: Whether to generate `__hash__` method.
        :param frozen: Whether class should be immutable.
        :param unsafe_hash: Whether to allow manual declaration of potentially unsafe `__hash__` method.
        :param order: Whether to generate order methods.
        :param match_args: Whether to generate `__match_args__`.
        """

        # Merge parameters.
        type.__setattr__(
            cls,
            "__params__",
            dict(
                cls.__params__,
                **dict(
                    (n, bool(v))
                    for n, v in {
                        "kw_only": kw_only,
                        "init": init,
                        "repr": repr,
                        "eq": eq,
                        "hash": hash,
                        "frozen": frozen,
                        "order": order,
                        "match_args": match_args,
                    }.items()
                    if v is not None
                )
            ),
        )

        # __init__.
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

        # __repr__.
        if cls.__params__.get("repr", True):
            if "__repr__" in cls.__dict__:
                error = "auto generated '__repr__' method can't be overriden without disabling 'repr' parameter"
                raise TypeError(error)
            type.__setattr__(
                cls,
                "__repr__",
                _make_repr(cls.__module__, cls.__fields__, cls.__name__, cls.__params__.get("kw_only", False)),
            )
        elif "__repr__" not in cls.__dict__:
            type.__setattr__(cls, "__repr__", object.__init__)

        # __eq__.
        if cls.__params__.get("eq", True):
            if "__eq__" in cls.__dict__:
                error = "auto generated '__eq__' method can't be overriden without disabling 'eq' parameter"
                raise TypeError(error)
            type.__setattr__(cls, "__eq__", _make_eq(cls.__module__, cls.__fields__, cls.__name__))
        elif "__eq__" not in cls.__dict__ and "__hash__" not in cls.__dict__:
            type.__setattr__(cls, "__eq__", object.__eq__)

        # __hash__.
        frozen_cls = cls.__params__.get("frozen", False)
        if cls.__params__.get("hash", True):
            if "__hash__" in cls.__dict__:
                error = (
                    "auto generated '__hash__' method can't be overriden without disabling parameters 'hash' & 'eq' "
                    "and enabling 'unsafe_hash'"
                )
                raise TypeError(error)
            type.__setattr__(cls, "__hash__", _make_hash(cls.__module__, cls.__fields__, cls.__name__, frozen_cls))
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

        # __setattr__ & __delattr__.
        for method, method_maker in (("__setattr__", _make_setattr), ("__delattr__", _make_delattr)):
            if frozen_cls or any(
                (f.frozen or f.converter is not None)
                for f in cls.__fields__.values()
                if (f.property is None or f.converter is not None)
            ):
                if method in cls.__dict__:
                    error = (
                        "auto generated '{}' method can't be overriden without disabling 'frozen' parameter "
                        "for class and all of its fields".format(method)
                    )
                    raise TypeError(error)
                type.__setattr__(cls, method, method_maker(cls.__module__, cls.__fields__, cls.__name__, frozen_cls))
            elif method not in cls.__dict__:
                type.__setattr__(cls, method, getattr(object, method))

        # order.
        for method_name, order_operator in _order_operators.items():
            if cls.__params__.get("order", False):
                if method_name in cls.__dict__:
                    error = "auto generated {!r} method can't be overriden without disabling 'order' parameter".format(
                        method_name
                    )
                    raise TypeError(error)
                type.__setattr__(
                    cls,
                    method_name,
                    _make_order(cls.__module__, cls.__fields__, cls.__name__, method_name),  # type: ignore
                )
            elif method_name not in cls.__dict__:
                type.__setattr__(cls, method_name, getattr(object, method_name))

        # __match_args__.
        if cls.__params__.get("match_args", True):
            if "__match_args__" in cls.__dict__:
                error = (
                    "auto generated '__match_args__' tuple can't be overriden without disabling 'match_args' parameter"
                )
                raise TypeError(error)
            type.__setattr__(cls, "__match_args__", _make_match_args(cls.__fields__))
        elif "__match_args__" not in cls.__dict__:
            type.__setattr__(cls, "__match_args__", ())

    def __init__(self, *args, **kwargs):
        pass

    def __post_init__(self):
        pass
