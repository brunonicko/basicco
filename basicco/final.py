"""Custom `final` decorator that enables runtime checking for classes and methods."""

import inspect
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

__all__ = ["final", "FinalMeta"]

_FINAL_CLASS_TAG = "__isfinalclass__"
_FINAL_METHOD_TAG = "__isfinalmethod__"

_FINAL_METHODS = "__finalmethods__"


__final = final


def _final(obj):
    # type: (FT) -> FT
    if inspect.isclass(obj):
        type.__setattr__(obj, _FINAL_CLASS_TAG, True)
    else:
        object.__setattr__(obj, _FINAL_METHOD_TAG, True)
    return __final(obj)


_final.__name__ = final.__name__
_final.__doc__ = final.__doc__
if hasattr(final, "__qualname__"):
    _final.__qualname__ = final.__qualname__
globals()["final"] = _final  # trick mypy


class FinalMeta(type):
    """Enables runtime-checking for `final` decorator."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(FinalMeta, cls).__init__(name, bases, dct, **kwargs)

        # Iterate over MRO of the class.
        final_cls = None  # type: Optional[Type]
        final_method_names = set()  # type: Set[str]
        for base in reversed(inspect.getmro(cls)):

            # Prevent subclassing final classes.
            if getattr(base, _FINAL_CLASS_TAG, False) is True:
                if final_cls is not None:
                    error = "can't subclass final class {}".format(
                        repr(final_cls.__name__)
                    )
                    raise TypeError(error)
                final_cls = base

            # Iterate over methods defined for this base.
            for method_name, method in iteritems(base.__dict__):

                # Can't override final methods.
                if method_name in final_method_names:
                    error = "can't override final method {}".format(repr(method_name))
                    raise TypeError(error)

                # Find final tag.
                is_final = False

                # Descriptor.
                if hasattr(method, "__get__"):
                    is_final |= getattr(method, _FINAL_METHOD_TAG, False)

                    # Has 'fget' getter (property-like).
                    if hasattr(method, "fget"):
                        is_final |= getattr(method.fget, _FINAL_METHOD_TAG, False)

                # Static or class method.
                if isinstance(method, (staticmethod, classmethod)):
                    is_final |= getattr(method.__func__, _FINAL_METHOD_TAG, False)

                # Regular method.
                if callable(method):
                    is_final |= getattr(method, _FINAL_METHOD_TAG, False)

                # Keep track of final methods.
                if is_final:
                    final_method_names.add(method_name)

            # Store final methods.
            type.__setattr__(cls, _FINAL_METHODS, frozenset(final_method_names))
