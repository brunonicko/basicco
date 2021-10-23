"""Matches Python 2 behavior with Python 3 for abstract members."""

from inspect import isclass, getmro
from abc import ABCMeta
from abc import abstractmethod as abstract
from typing import TYPE_CHECKING

from six import iteritems

if TYPE_CHECKING:
    from typing import Set, TypeVar

    AT = TypeVar("AT", bound="AbstractMeta")

__all__ = ["abstract", "is_abstract", "is_abstract_member", "AbstractMeta"]

_ABSTRACT_CLASS_TAG = "__isabstractclass__"
_ABSTRACT_METHOD_TAG = "__isabstractmethod__"
_ABSTRACT_METHODS = "__abstractmethods__"


__abstract = abstract


def _abstract(obj):
    # type: (AT) -> AT
    if isclass(obj):
        super_new = obj.__dict__.get("__new__")
        if isinstance(super_new, staticmethod):
            super_new = super_new.__func__

        def __new__(cls, *args, **kwargs):
            if cls.__dict__.get(_ABSTRACT_CLASS_TAG, False):
                abstract_members = sorted(getattr(cls, _ABSTRACT_METHODS, ()))
                if abstract_members:
                    error = (
                        "can't instantiate abstract class {} with abstract members {}"
                    ).format(
                        repr(cls.__name__),
                        ", ".join(repr(m) for m in abstract_members),
                    )
                else:
                    error = "can't instantiate abstract class {}".format(
                        repr(cls.__name__)
                    )
                raise TypeError(error)
            elif super_new is not None:
                return super_new(cls, *args, **kwargs)
            else:
                return super(obj, cls).__new__(cls, *args, **kwargs)

        type.__setattr__(obj, "__new__", staticmethod(__new__))
        type.__setattr__(obj, _ABSTRACT_CLASS_TAG, True)

        return obj

    else:
        return __abstract(obj)


_abstract.__name__ = abstract.__name__
_abstract.__doc__ = abstract.__doc__
if hasattr(abstract, "__qualname__"):
    _abstract.__qualname__ = abstract.__qualname__
globals()["abstract"] = _abstract  # trick mypy


def is_abstract(obj):
    if isclass(obj):
        return obj.__dict__.get(_ABSTRACT_CLASS_TAG, False) or bool(
            getattr(obj, _ABSTRACT_METHODS, ())
        )
    else:
        return is_abstract_member(obj)


def is_abstract_member(obj):

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


class AbstractMeta(ABCMeta):
    """Finds abstract members in properties and descriptors for both Python 2 and 3."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(AbstractMeta, cls).__init__(name, bases, dct, **kwargs)

        # Iterate over MRO of the class.
        abstract_method_names = set(
            getattr(cls, _ABSTRACT_METHODS, ())
        )  # type: Set[str]
        for base in reversed(getmro(cls)):

            # Find abstract members.
            for member_name, member in iteritems(base.__dict__):

                # Keep track.
                if is_abstract_member(member):
                    abstract_method_names.add(member_name)
                else:
                    abstract_method_names.discard(member_name)

        # Update class information.
        type.__setattr__(cls, _ABSTRACT_METHODS, frozenset(abstract_method_names))

    # TODO: change members at runtime
