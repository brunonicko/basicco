"""Read-only wrapped dictionary implementation."""

from abc import ABCMeta
from copy import deepcopy
from typing import TYPE_CHECKING, Generic, TypeVar, overload

try:
    from typing import GenericMeta as _GenericMeta  # type: ignore
except ImportError:
    _GenericMeta = type

from six import with_metaclass
from six.moves import collections_abc

from .generic_meta import GenericMeta

if TYPE_CHECKING:
    from typing import Any, Optional, Mapping, Dict, Iterator

__all__ = ["WrappedDict"]


KT = TypeVar("KT")
VT = TypeVar("VT")
FD = TypeVar("FD", bound="WrappedDict")

_WRAPPED = "__wrapped__"
_EMPTY = object()
_init = lambda s, w: object.__setattr__(s, _WRAPPED, w)
_read = lambda s: object.__getattribute__(s, _WRAPPED)


if _GenericMeta is type:

    class WrappedDictMeta(ABCMeta):
        pass

else:

    class WrappedDictMeta(GenericMeta, ABCMeta):  # type: ignore
        pass


class WrappedDict(
    with_metaclass(GenericMeta, collections_abc.Mapping, Generic[KT, VT])
):
    """Read-only Wrapped dictionary."""

    __slots__ = (_WRAPPED,)
    __hash__ = None  # type: ignore

    def __init__(self, mapping=None):
        # type: (Optional[Mapping[KT, VT]]) -> None
        if mapping is None:
            mapping = {}
        _init(self, mapping)

    def __copy__(self):
        # type: (FD) -> FD
        return type(self)(_read(self).copy())

    def __deepcopy__(self, memo=None):
        # type: (FD, Optional[Dict[int, Any]]) -> FD
        if memo is None:
            memo = {}
        self_id = id(self)
        try:
            deep_copied = memo[self_id]
        except KeyError:
            cls = type(self)
            deep_copied = memo[self_id] = cls.__new__(cls)
            _init(deep_copied, deepcopy(_read(self), memo))
        return deep_copied

    def __eq__(self, other):
        # type: (object) -> bool
        if isinstance(other, WrappedDict):
            return _read(self) == _read(other)
        elif isinstance(other, dict):
            return _read(self) == other
        else:
            return False

    def __ne__(self, other):
        # type: (object) -> bool
        return not self.__eq__(other)

    def __reduce__(self):
        return type(self), (_read(self),)

    def __getitem__(self, key):
        # type: (KT) -> VT
        return getattr(self, _WRAPPED)[key]

    def __len__(self):
        # type: () -> int
        return len(getattr(self, _WRAPPED))

    def __iter__(self):
        # type: () -> Iterator[KT]
        for key in getattr(self, _WRAPPED):
            yield key

    def __repr__(self):
        # type: () -> str
        return "{}({})".format(type(self).__name__, repr(_read(self)))

    def __setattr__(self, name, value):
        error = "can't set '{}' attribute".format(name)
        raise AttributeError(error)

    def __delattr__(self, name):
        error = "can't delete '{}' attribute".format(name)
        raise AttributeError(error)

    def clear(self):
        # type: (FD) -> FD
        return type(self)()

    def copy(self):
        # type: (FD) -> FD
        return self.__copy__()

    def set(self, key, value):
        # type: (FD, KT, VT) -> FD
        new_self = self.__copy__()
        _read(new_self)[key] = value
        return new_self

    @overload
    def update(self, m, **k):
        # type: (FD, Mapping[KT, VT], **VT) -> FD
        pass

    @overload
    def update(self, **k):
        # type: (FD, **VT) -> FD
        pass

    def update(self, *args, **kwargs):
        updates = {}
        if args:
            if len(args) == 1:
                updates.update(args[0])
            else:
                error = "update expected at most 1 argument, got {}".format(len(args))
                raise TypeError(error)
        updates.update(kwargs)
        new_self = self.__copy__()
        _read(new_self).update(updates)
        return new_self

    def delete(self, key):
        # type: (FD, KT) -> FD
        new_self = self.__copy__()
        del _read(new_self)[key]
        return new_self

    def discard(self, key):
        # type: (FD, KT) -> FD
        try:
            return self.delete(key)
        except KeyError:
            return self
