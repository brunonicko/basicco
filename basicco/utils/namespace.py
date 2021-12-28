"""Namespace/Bunch-like object."""

from re import compile as re_compile
from copy import deepcopy
from typing import TYPE_CHECKING

from six import string_types, iteritems

if TYPE_CHECKING:
    from typing import Any, Optional, Mapping, Union

__all__ = ["ReadOnlyNamespace", "Namespace"]


_WRAPPED = "__wrapped__"
_MEMBER = re_compile(r"^[a-zA-Z_]\w*$")
_init = lambda s, w: object.__setattr__(s, _WRAPPED, w)
_read = lambda s: object.__getattribute__(s, _WRAPPED)


class ReadOnlyNamespace(object):
    """Wraps a mapping and provides read-only attribute-style access to it."""

    __slots__ = (_WRAPPED, "__weakref__")
    __hash__ = None  # type: ignore

    def __init__(self, wraps=None):
        # type: (Optional[Union[Mapping[str, Any], ReadOnlyNamespace]]) -> None
        if wraps is None:
            wraps = {}
        elif isinstance(wraps, ReadOnlyNamespace):
            wraps = _read(wraps)
        _init(self, wraps)

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
            deep_copy_args = (_read(self), memo)
            _init(deep_copied, deepcopy(*deep_copy_args))
        return deep_copied

    def __reduce__(self):
        return type(self), (_read(self),)

    def __eq__(self, other):
        return isinstance(other, ReadOnlyNamespace) and _read(other) == _read(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "{}({})".format(type(self).__name__, repr(_read(self)))

    def __contains__(self, name):
        return name in _read(self)

    def __iter__(self):
        for name, value in iteritems(_read(self)):
            yield name, value

    def __len__(self):
        return len(_read(self))

    def __getitem__(self, name):
        return _read(self)[name]

    def __dir__(self):
        cls = type(self)
        return sorted(
            m
            for m in _read(self)
            if isinstance(m, string_types) and not hasattr(cls, m) and _MEMBER.match(m)
        )

    def __getattribute__(self, name):
        cls = type(self)
        if hasattr(cls, name):
            return object.__getattribute__(self, name)
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        cls = type(self)
        if hasattr(cls, name):
            member = getattr(cls, name)
            if hasattr(member, "__set__"):
                object.__setattr__(self, name, value)
            else:
                error = "can't change '{}' attribute/method".format(name)
                raise AttributeError(error)
        else:
            error = "read_only namespace, can't set attribute"
            raise AttributeError(error)

    def __delattr__(self, name):
        cls = type(self)
        if hasattr(cls, name):
            member = getattr(cls, name)
            if hasattr(member, "__delete__"):
                object.__delattr__(self, name)
            else:
                error = "can't delete '{}' attribute/method".format(name)
                raise AttributeError(error)
        else:
            error = "read_only namespace, can't delete attribute"
            raise AttributeError(error)


class Namespace(ReadOnlyNamespace):
    """Wraps a mapping and provides attribute-style access to it."""

    __slots__ = ()

    def __init__(self, wraps=None):
        # type: (Optional[Union[Mapping[str, Any], ReadOnlyNamespace]]) -> None
        if isinstance(wraps, ReadOnlyNamespace) and not isinstance(wraps, Namespace):
            wraps = dict(_read(wraps))
        super(Namespace, self).__init__(wraps=wraps)

    def __setitem__(self, name, value):
        _read(self)[name] = value

    def __delitem__(self, name):
        del _read(self)[name]

    def __setattr__(self, name, value):
        cls = type(self)
        if hasattr(cls, name):
            member = getattr(cls, name)
            if hasattr(member, "__set__"):
                object.__setattr__(self, name, value)
            else:
                error = "can't change '{}' attribute/method".format(name)
                raise AttributeError(error)
        else:
            _read(self)[name] = value

    def __delattr__(self, name):
        cls = type(self)
        if hasattr(cls, name):
            member = getattr(cls, name)
            if hasattr(member, "__delete__"):
                object.__delattr__(self, name)
            else:
                error = "can't delete '{}' attribute/method".format(name)
                raise AttributeError(error)
        else:
            try:
                del _read(self)[name]
            except KeyError:
                raise AttributeError(name)
