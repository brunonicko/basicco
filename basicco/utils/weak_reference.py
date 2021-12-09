"""Weak Reference-like object that supports pickling."""

from copy import deepcopy
from typing import TYPE_CHECKING, Generic, TypeVar
from weakref import WeakValueDictionary, ref

from six import with_metaclass

from .recursive_repr import recursive_repr
from .generic_meta import GenericMeta

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, Type

__all__ = ["WeakReference"]


T = TypeVar("T")  # Any type.

_DEAD_REF = ref(
    type("Dead", (object,), {"__slots__": ("__weakref__",)})()
)

_cache = (
    {}
)  # type: Dict[Type["WeakReference"], WeakValueDictionary[int, "WeakReference"]]


def _reduce_dead(cls):
    self = super(WeakReference, cls).__new__(cls)  # type: ignore
    self.__init__(None)
    return self


class WeakReference(with_metaclass(GenericMeta, Generic[T])):
    """
    Weak Reference-like object that supports pickling.

    .. code:: python

        >>> from basicco.utils.weak_reference import WeakReference
        >>> class MyClass(object):
        ...     pass
        ...
        >>> strong = MyClass()
        >>> weak = WeakReference(strong)
        >>> weak() is strong
        True
        >>> del strong
        >>> weak() is None
        True

    :param obj: Object to reference.
    """

    __slots__ = ("__weakref__", "__ref")

    @staticmethod
    def __new__(cls, obj=None):
        # type: (Type[WeakReference[T]], T) -> WeakReference[T]
        cache = _cache.setdefault(cls, WeakValueDictionary())
        if obj is None:
            obj_ref = _DEAD_REF
        else:
            obj_ref = ref(obj)

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
        # type: (T) -> None
        if obj is None:
            self.__ref = _DEAD_REF
        else:
            self.__ref = ref(obj)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        self_id = id(self)
        try:
            copy = memo[self_id]
        except KeyError:
            cls = type(self)
            obj = self()
            if self is WeakReference():
                assert obj is None
                copy = memo[self_id] = self
            elif obj is None:
                copy = memo[self_id] = _reduce_dead(cls)
            else:
                copy = memo[self_id] = cls(deepcopy(obj, memo))  # type: ignore
        return copy

    def __hash__(self):
        """
        Get hash.

        :return: Hash.
        :rtype: int
        """
        return hash(self.__ref)

    def __eq__(self, other):
        # type: (Any) -> bool
        """
        Compare for equality.

        :param other: Other.

        :return: True if equal.
        :rtype: bool or NotImplemented
        """
        return self is other

    def __ne__(self, other):
        # type: (Any) -> bool
        """
        Compare for inequality.

        :param other: Other.

        :return: True if not equal.
        :rtype: bool or NotImplemented
        """
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    @recursive_repr
    def __repr__(self):
        # type: () -> str
        """
        Get representation.

        :return: Representation.
        :rtype: str
        """
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
        # type: () -> str
        """
        Get string representation.

        :return: String representation.
        :rtype: str
        """
        return self.__repr__()

    def __call__(self):
        # type: () -> Optional[T]
        """
        Get strong reference to the object or None if no longer alive.

        :return: Strong reference or `None`.
        :rtype: object or None
        """
        return self.__ref()

    def __reduce__(self):
        cls = type(self)
        obj = self()
        if self is WeakReference():
            assert obj is None
            return cls, (None,)
        if obj is None:
            return _reduce_dead, (cls,)
        return cls, (obj,)
