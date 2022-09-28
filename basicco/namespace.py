"""Namespace/Bunch-like object."""

import copy
import re

import six
from tippo import Any, Iterable, Iterator, Mapping, Tuple, TypeVar

from .mangling import mangle

__all__ = ["Namespace", "MutableNamespace", "NamespacedMeta", "Namespaced"]


_VT = TypeVar("_VT")

_WRAPPED_SLOT = "__wrapped__"
_MEMBER_REGEX = re.compile(r"^[a-zA-Z_]\w*$")
_init = lambda s, w: object.__setattr__(s, _WRAPPED_SLOT, w)
_read = lambda s: object.__getattribute__(s, _WRAPPED_SLOT)


class Namespace(Iterable[Tuple[str, _VT]]):
    """Read-only namespace that wraps a mapping."""

    __slots__ = (_WRAPPED_SLOT,)
    __hash__ = None  # type: ignore

    def __init__(self, wrapped=None):
        # type: (Mapping[str, _VT] | Namespace[_VT] | None) -> None
        """
        :param wrapped: Mapping/Namespace to be wrapped.
        """
        if wrapped is None:
            wrapped = {}
        elif isinstance(wrapped, Namespace):
            wrapped = _read(wrapped)
        _init(self, wrapped)

    def __getitem__(self, name):
        return _read(self)[name]

    def __dir__(self):
        keys = {k for k in _read(self) if isinstance(k, str) and not hasattr(type(self), k) and _MEMBER_REGEX.match(k)}
        return sorted(keys)

    def __eq__(self, other):
        return isinstance(other, Namespace) and _read(other) == _read(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "{}({})".format(type(self).__name__, _read(self))

    def __reduce__(self):
        return type(self), (_read(self),)

    def __copy__(self):
        return type(self)(_read(self).copy())

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        self_id = id(self)
        try:
            deep_copied = memo[self_id]
        except KeyError:
            cls = type(self)
            deep_copied = memo[self_id] = cls.__new__(cls)
            _init(deep_copied, copy.deepcopy(_read(self), memo))
        return deep_copied

    def __len__(self):
        # type: () -> int
        return len(_read(self))

    def __iter__(self):
        # type: () -> Iterator[tuple[str, _VT]]
        for key, value in _read(self).items():
            yield key, value

    def __contains__(self, name):
        # type: (str) -> bool
        return name in _read(self)

    def __getattribute__(self, name):
        # type: (str) -> _VT
        cls = type(self)
        if hasattr(cls, name):
            return object.__getattribute__(self, name)
        try:
            return _read(self)[name]
        except KeyError:
            raise AttributeError(name)


class MutableNamespace(Namespace[_VT]):
    """Mutable namespace that wraps a mapping."""

    __slots__ = ()

    def __setitem__(self, name, value):
        _read(self)[name] = value

    def __delitem__(self, name):
        del _read(self)[name]

    def __setattr__(self, name, value):
        # type: (str, _VT) -> None
        cls = type(self)
        if hasattr(cls, name):
            member = getattr(cls, name)
            if hasattr(member, "__set__"):
                object.__setattr__(self, name, value)
            else:
                error = "can't change '{!r}' attribute/method".format(name)
                raise AttributeError(error)
        else:
            _read(self)[name] = value

    def __delattr__(self, name):
        # type: (str) -> None
        cls = type(self)
        if hasattr(cls, name):
            member = getattr(cls, name)
            if hasattr(member, "__delete__"):
                object.__delattr__(self, name)
            else:
                error = "can't delete '{!r}' attribute/method".format(name)
                raise AttributeError(error)
        else:
            try:
                del _read(self)[name]
            except KeyError:
                exc = AttributeError(name)
                six.raise_from(exc, None)
                raise exc


class NamespacedMeta(type):
    """Metaclass that provides a mutable `__namespace` as a protected class attribute."""

    __namespace = MutableNamespace()  # type: MutableNamespace[Any]

    def __getattr__(cls, name):
        # type: (str) -> Any
        namespace_attr = mangle("__namespace", cls.__name__)
        if name == namespace_attr:
            namespace = MutableNamespace()  # type: MutableNamespace[Any]
            type.__setattr__(cls, namespace_attr, namespace)
            return namespace
        try:
            return super(NamespacedMeta, cls).__getattr__(name)  # type: ignore  # noqa
        except AttributeError:
            pass
        error = "class {!r} has no attribute {!r}".format(cls.__name__, name)
        raise AttributeError(error)


type.__delattr__(NamespacedMeta, mangle("__namespace", NamespacedMeta.__name__))


class Namespaced(six.with_metaclass(NamespacedMeta, object)):
    """Class that provides a mutable `__namespace` as a protected class attribute."""

    __slots__ = ()
