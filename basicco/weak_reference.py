"""Weak Reference-like object that supports pickling."""

import copy
import threading
import weakref

from tippo import Any, Generic, Type, TypeVar

from .recursive_repr import recursive_repr

__all__ = ["WeakReference", "UniqueHashWeakReference"]


_T = TypeVar("_T")

_DEAD_REF = weakref.ref(type("Dead", (object,), {"__slots__": ("__weakref__",)})())

_cache = {}  # type: dict[Type["WeakReference"], weakref.WeakValueDictionary[int, "WeakReference"]]

_lock = threading.RLock()


def _reduce_dead(cls):
    self = super(WeakReference, cls).__new__(cls)  # type: ignore
    self.__init__(None)  # type: ignore
    return self


class WeakReference(Generic[_T]):
    """Weak Reference-like object that supports pickling."""

    __slots__ = ("__weakref__", "__ref")

    @staticmethod
    def __new__(cls, obj=None):
        # type: (Type[WeakReference[_T]], _T) -> WeakReference[_T]
        with _lock:
            cache = _cache.setdefault(cls, weakref.WeakValueDictionary())
            if obj is None:
                obj_ref = _DEAD_REF
            else:
                obj_ref = weakref.ref(obj)

            obj_ref_id = id(obj_ref)
            try:
                self = cache[obj_ref_id]
            except KeyError:
                pass
            else:
                try:
                    if self.__ref is obj_ref:
                        return self
                except ReferenceError:
                    pass

            self = cache[obj_ref_id] = super(WeakReference, cls).__new__(cls)
            return self

    def __init__(self, obj=None):
        # type: (_T | None) -> None
        """
        :param obj: Object to reference.
        """
        if obj is None:
            self.__ref = _DEAD_REF
        else:
            self.__ref = weakref.ref(obj)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        self_id = id(self)
        try:
            dup = memo[self_id]
        except KeyError:
            cls = type(self)
            obj = self()
            if self is type(self)():
                assert obj is None
                dup = memo[self_id] = self
            elif obj is None:
                dup = memo[self_id] = _reduce_dead(cls)
            else:
                dup = memo[self_id] = cls(copy.deepcopy(obj, memo))
        return dup

    def __hash__(self):
        return hash(self.__ref)

    def __eq__(self, other):
        # type: (Any) -> bool
        return self is other

    def __ne__(self, other):
        # type: (Any) -> bool
        return not self.__eq__(other)

    @recursive_repr
    def __repr__(self):
        obj = self()
        return "<{} object at {}; {}>".format(
            type(self).__name__,
            hex(id(self)),
            "dead"
            if obj is None
            else "to '{}' at {}".format(
                type(obj).__name__,
                hex(id(obj)),
            ),
        )

    def __str__(self):
        return self.__repr__()

    def __call__(self):
        # type: () -> _T | None
        """
        Get strong reference to the object or None if no longer alive.

        :return: Strong reference or `None`.
        """
        return self.__ref()

    def __reduce__(self):
        cls = type(self)
        obj = self()
        if self is type(self)():
            assert obj is None
            return cls, (None,)
        if obj is None:
            return _reduce_dead, (cls,)
        return cls, (obj,)


class UniqueHashWeakReference(WeakReference[_T]):
    """Weak Reference-like object that supports pickling and has a unique id-based hash."""

    __slots__ = ()

    def __hash__(self):
        return object.__hash__(self)
