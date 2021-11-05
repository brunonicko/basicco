"""Custom `final` decorator that enables runtime checking for classes and methods."""

from inspect import isclass, getmro
from functools import wraps
from typing import TYPE_CHECKING

try:
    from typing import final
except ImportError:
    final = lambda f: f

from six import iteritems

if TYPE_CHECKING:
    from typing import TypeVar, Optional, Type, Set

    T = TypeVar("T")
    FT = TypeVar("FT", bound="FinalMeta")

__all__ = ["final", "is_final", "is_final_member", "FinalMeta"]

_FINAL_CLASS_TAG = "__isfinalclass__"
_FINAL_METHOD_TAG = "__isfinalmethod__"

_FINAL_METHODS = "__finalmethods__"


__final = final


def _final(obj):
    # type: (FT) -> FT
    if isclass(obj):
        type.__setattr__(obj, _FINAL_CLASS_TAG, True)
    else:
        object.__setattr__(obj, _FINAL_METHOD_TAG, True)
    return __final(obj)


globals()["final"] = wraps(final)(_final)  # trick IDEs/static type checkers


def is_final(obj):
    if isclass(obj):
        return getattr(obj, _FINAL_CLASS_TAG, False)
    else:
        return is_final_member(obj)


def is_final_member(member):
    _is_final = False

    # Descriptor.
    if hasattr(member, "__get__"):
        _is_final |= getattr(member, _FINAL_METHOD_TAG, False)

        # Has 'fget' getter (property-like).
        if hasattr(member, "fget"):
            _is_final |= getattr(member.fget, _FINAL_METHOD_TAG, False)

    # Static or class method.
    if isinstance(member, (staticmethod, classmethod)):
        _is_final |= getattr(member.__func__, _FINAL_METHOD_TAG, False)

    # Regular method.
    if callable(member):
        _is_final |= getattr(member, _FINAL_METHOD_TAG, False)

    return _is_final


class FinalMeta(type):
    """Enables runtime-checking for `final` decorator."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(FinalMeta, cls).__init__(name, bases, dct, **kwargs)
        cls.__gather_final_members()

    def __gather_final_members(cls):

        # Iterate over MRO of the class.
        final_cls = None  # type: Optional[Type]
        final_member_names = set()  # type: Set[str]
        for base in reversed(getmro(cls)):

            # Prevent subclassing final classes.
            if getattr(base, _FINAL_CLASS_TAG, False) is True:
                if final_cls is not None:
                    error = "can't subclass final class {}".format(
                        repr(final_cls.__name__)
                    )
                    raise TypeError(error)
                final_cls = base

            # Find final members.
            for member_name, member in iteritems(base.__dict__):

                # Can't override final members.
                if member_name in final_member_names:
                    error = "can't override final member {}".format(repr(member_name))
                    raise TypeError(error)

                # Keep track of final members.
                if is_final_member(member):
                    final_member_names.add(member_name)

            # Store final methods.
            type.__setattr__(cls, _FINAL_METHODS, frozenset(final_member_names))

    def __setattr__(cls, name, value):
        super(FinalMeta, cls).__setattr__(name, value)
        cls.__gather_final_members()

    def __delattr__(cls, name):
        super(FinalMeta, cls).__delattr__(name)
        cls.__gather_final_members()
