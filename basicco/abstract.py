"""Matches Python 2 behavior with Python 3 for abstract members."""

import inspect
from abc import ABCMeta
from abc import abstractmethod as abstract
from typing import TYPE_CHECKING

from six import iteritems

if TYPE_CHECKING:
    from typing import Set, TypeVar

    AT = TypeVar("AT", bound="AbstractMeta")

__all__ = ["abstract", "is_abstract", "AbstractMeta"]

_ABSTRACT_METHOD_TAG = "__isabstractmethod__"
_ABSTRACT_METHODS = "__abstractmethods__"


__abstract = abstract


def _abstract(obj):
    # type: (AT) -> AT
    if inspect.isclass(obj):
        error = "'abstract' decorator should not be used on classes"
        raise TypeError(error)
    return __abstract(obj)


_abstract.__name__ = abstract.__name__
_abstract.__doc__ = abstract.__doc__
if hasattr(abstract, "__qualname__"):
    _abstract.__qualname__ = abstract.__qualname__
globals()["abstract"] = _abstract  # trick mypy


def is_abstract(member):
    _is_abstract = False

    # Descriptor.
    if hasattr(member, "__get__"):
        _is_abstract |= getattr(member, _ABSTRACT_METHOD_TAG, False)

        # Has 'fget' getter (property-like).
        if hasattr(member, "fget"):
            _is_abstract |= getattr(member.fget, _ABSTRACT_METHOD_TAG, False)

    # Static or class method.
    if isinstance(member, (staticmethod, classmethod)):
        _is_abstract |= getattr(member.__func__, _ABSTRACT_METHOD_TAG, False)

    # Regular method.
    if callable(member):
        _is_abstract |= getattr(member, _ABSTRACT_METHOD_TAG, False)

    return _is_abstract


class AbstractMeta(ABCMeta):
    """Finds abstract members in properties and descriptors for both Python 2 and 3."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(AbstractMeta, cls).__init__(name, bases, dct, **kwargs)

        # Iterate over MRO of the class.
        abstract_method_names = set(
            getattr(cls, _ABSTRACT_METHODS, ())
        )  # type: Set[str]
        for base in reversed(inspect.getmro(cls)):

            # Find abstract members.
            for member_name, member in iteritems(base.__dict__):

                # Keep track.
                if is_abstract(member):
                    abstract_method_names.add(member_name)
                else:
                    abstract_method_names.discard(member_name)

        # Update class information.
        type.__setattr__(cls, _ABSTRACT_METHODS, frozenset(abstract_method_names))

    # TODO: change members at runtime
