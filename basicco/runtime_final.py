"""Custom `final` decorator that enables runtime checking for classes and methods."""

import functools
import inspect

import six
from tippo import Callable, Type, TypeVar, final

from .get_mro import get_mro

__all__ = ["final", "is_final", "RuntimeFinalMeta", "RuntimeFinal"]


_T = TypeVar("_T")
_FINAL_CLASS_TAG = "__is_final_class__"
_FINAL_METHOD_TAG = "__is_final_method__"
_FINAL_METHODS = "__final_methods__"


__final = final


def _final(obj):
    if inspect.isclass(obj):
        if not isinstance(obj, RuntimeFinalMeta):
            error = "class {!r} doesn't have {!r} as its metaclass".format(obj.__name__, RuntimeFinalMeta.__name__)
            raise TypeError(error)
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


def is_final(obj):
    # type: (Callable) -> bool
    """
    Tell whether a class or member is final.

    :param obj: Class or member.
    :return: True if final.
    """
    if inspect.isclass(obj):
        return getattr(obj, _FINAL_CLASS_TAG, False)
    else:
        return _is_final_member(obj)


class RuntimeFinalMeta(type):
    """Metaclass that enables runtime-checking for `final` decorator."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(RuntimeFinalMeta, cls).__init__(name, bases, dct, **kwargs)
        cls.__gather_final_members()

    def __gather_final_members(cls):

        # Iterate over MRO of the class.
        final_cls = None  # type: Type | None
        final_member_names = {}  # type: dict[str, Type]
        mro = get_mro(cls)
        for base in reversed(mro):
            if base is object:
                continue

            # Prevent subclassing final classes.
            if getattr(base, _FINAL_CLASS_TAG, False) is True:
                if final_cls is not None:
                    error = "can't subclass final class {!r}".format(final_cls.__name__)
                    raise TypeError(error)
                final_cls = base

            # Find final members.
            for member_name, member in base.__dict__.items():

                # Can't override final members.
                if member_name in final_member_names:
                    error = "{!r} overrides final member {!r} defined by {!r}".format(
                        base.__name__,
                        member_name,
                        final_member_names[member_name].__name__,
                    )
                    raise TypeError(error)

                # Keep track of final members.
                if _is_final_member(member):
                    final_member_names[member_name] = base

            # Store final members.
            type.__setattr__(cls, _FINAL_METHODS, frozenset(final_member_names))

    def __setattr__(cls, name, value):
        super(RuntimeFinalMeta, cls).__setattr__(name, value)
        if is_final(value):
            cls.__gather_final_members()

    def __delattr__(cls, name):
        gather = False
        for base in get_mro(cls):
            if name in base.__dict__:
                gather = is_final(base.__dict__[name])
                break
        super(RuntimeFinalMeta, cls).__delattr__(name)
        if gather:
            cls.__gather_final_members()


class RuntimeFinal(six.with_metaclass(RuntimeFinalMeta, object)):
    """Class that enables runtime-checking for `final` decorator."""

    __slots__ = ()
