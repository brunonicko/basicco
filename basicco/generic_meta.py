"""Improved compatibility with `typing.Generic` for Python 2.7."""

try:
    from typing import GenericMeta as _GenericMeta  # type: ignore
except ImportError:
    _GenericMeta = type

__all__ = ["GenericMeta"]


if _GenericMeta is not type:

    class GenericMeta(_GenericMeta):

        # Fix not equal operator logic in python 2.
        def __ne__(cls, other):
            # type: (object) -> bool
            is_equal = cls.__eq__(other)
            if is_equal is NotImplemented:
                return NotImplemented
            else:
                return not is_equal

        # Fix subclassing slotted generic class with __weakref__.
        def __getitem__(cls, params):
            slots = getattr(cls, "__slots__", None)
            if slots is not None and "__weakref__" in slots:
                type.__setattr__(cls, "__slots__", tuple(s for s in slots if s != "__weakref__"))
                try:
                    return super(GenericMeta, cls).__getitem__(params)  # type: ignore
                finally:
                    type.__setattr__(cls, "__slots__", slots)
            else:
                return super(GenericMeta, cls).__getitem__(params)  # type: ignore

else:
    GenericMeta = type  # type: ignore
