"""Custom `final` decorator that enables runtime checking for classes and methods."""

import inspect
import functools
from typing import TypeVar, Optional, Type, Set, Callable

try:
    from typing import final
except ImportError:
    final = lambda f: f  # type: ignore

__all__ = ["final", "is_final", "FinalizedMeta"]


_T = TypeVar("_T")
_FINAL_CLASS_TAG = "__is_final_class__"
_FINAL_METHOD_TAG = "__is_final_method__"
_FINAL_METHODS = "__final_methods__"


__final = final


def _final(obj):
    if inspect.isclass(obj):
        if not isinstance(obj, FinalizedMeta):
            raise TypeError(f"class {obj.__name__!r} doesn't have {FinalizedMeta.__name__!r} as its metaclass")
        type.__setattr__(obj, _FINAL_CLASS_TAG, True)
    else:
        object.__setattr__(obj, _FINAL_METHOD_TAG, True)
    return __final(obj)


globals()["final"] = functools.wraps(final)(_final)  # trick IDEs/static type checkers
globals()["final"].__doc__ = "A decorator to indicate final methods and final classes."


def _is_final_member(member):
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


def is_final(obj: Callable) -> bool:
    """
    Tell whether a class/method is final.

    :param obj: Class or method.
    :return: True if final.
    """
    if inspect.isclass(obj):
        return getattr(obj, _FINAL_CLASS_TAG, False)
    else:
        return _is_final_member(obj)


class FinalizedMeta(type):
    """Metaclass that enables runtime-checking for `final` decorator."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(FinalizedMeta, cls).__init__(name, bases, dct, **kwargs)
        cls.__gather_final_members()

    def __gather_final_members(cls):

        # Iterate over MRO of the class.
        final_cls = None  # type: Optional[Type]
        final_member_names = set()  # type: Set[str]
        for base in reversed(inspect.getmro(cls)[:-1]):

            # Prevent subclassing final classes.
            if getattr(base, _FINAL_CLASS_TAG, False) is True:
                if final_cls is not None:
                    raise TypeError(f"can't subclass final class {final_cls.__name__!r}")
                final_cls = base

            # Find final members.
            for member_name, member in base.__dict__.items():

                # Can't override final members.
                if member_name in final_member_names:
                    raise TypeError(f"can't override final member {member_name!r}")

                # Keep track of final members.
                if _is_final_member(member):
                    final_member_names.add(member_name)

            # Store final methods.
            type.__setattr__(cls, _FINAL_METHODS, frozenset(final_member_names))

    def __setattr__(cls, name, value):
        super(FinalizedMeta, cls).__setattr__(name, value)
        cls.__gather_final_members()

    def __delattr__(cls, name):
        super(FinalizedMeta, cls).__delattr__(name)
        cls.__gather_final_members()
