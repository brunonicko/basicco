"""
Better matches Python 3.7+ behavior for
`abstract members <https://docs.python.org/3/library/abc.html>`_.
"""

import abc
from abc import abstractmethod as abstract

import six
from tippo import Any, Dict, Set, Tuple, Type, TypeVar

from .get_mro import get_mro

__all__ = ["ABC", "abstract", "is_abstract", "AbstractMeta", "Abstract"]


_T = TypeVar("_T")

_ABSTRACT_METHOD_TAG = "__isabstractmethod__"
_ABSTRACT_METHODS = "__abstractmethods__"


try:
    ABC = abc.ABC
except AttributeError:
    ABC = object  # type: ignore


def is_abstract(obj):
    # type: (Any) -> bool
    """
    Tells whether a member is abstract.

    :param obj: Member.
    :return: True if abstract.
    """
    _is_abstract = False

    # Descriptor.
    if hasattr(obj, "__get__"):
        _is_abstract |= getattr(obj, _ABSTRACT_METHOD_TAG, False)

        # Has 'fget' getter (property-like).
        if hasattr(obj, "fget"):
            _is_abstract |= getattr(obj.fget, _ABSTRACT_METHOD_TAG, False)

    # Static or class method.
    if isinstance(obj, (staticmethod, classmethod)):
        _is_abstract |= getattr(obj.__func__, _ABSTRACT_METHOD_TAG, False)

    # Regular method.
    if callable(obj):
        _is_abstract |= getattr(obj, _ABSTRACT_METHOD_TAG, False)

    return _is_abstract


class AbstractMeta(abc.ABCMeta):
    """Finds abstract members in properties and descriptors."""

    def __init__(cls, name, bases, dct, **kwargs):
        # type: (str, Tuple[Type[Any], ...], Dict[str, Any], **Any) -> None
        super(AbstractMeta, cls).__init__(name, bases, dct, **kwargs)  # noqa
        cls.__gather_abstract_members()

    def __gather_abstract_members(cls):
        # type: () -> None

        # Iterate over MRO of the class.
        abstract_method_names = set()  # type: Set[str]
        for base in reversed(get_mro(cls)):
            # Find abstract members.
            for member_name, member in six.iteritems(base.__dict__):
                # Keep track.
                if is_abstract(member):
                    abstract_method_names.add(member_name)
                else:
                    abstract_method_names.discard(member_name)

        # Update class information.
        type.__setattr__(cls, _ABSTRACT_METHODS, frozenset(abstract_method_names))

    def __setattr__(cls, name, value):
        # type: (str, Any) -> None
        super(AbstractMeta, cls).__setattr__(name, value)
        if name in cls.__dict__ and is_abstract(cls.__dict__[name]):
            cls.__gather_abstract_members()

    def __delattr__(cls, name):
        # type: (str) -> None
        gather = False
        for base in get_mro(cls):
            if name in base.__dict__:
                gather = is_abstract(base.__dict__[name])
                break
        super(AbstractMeta, cls).__delattr__(name)
        if gather:
            cls.__gather_abstract_members()


class Abstract(six.with_metaclass(AbstractMeta, ABC)):
    """Finds abstract members in properties and descriptors."""

    __slots__ = ()
