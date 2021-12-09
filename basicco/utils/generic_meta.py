"""Improved compatibility with `typing.Generic` for Python 2.7."""

try:
    from typing import GenericMeta as _GenericMeta  # type: ignore
except ImportError:
    _GenericMeta = type

__all__ = ["GenericMeta"]


if _GenericMeta is not type:
    class GenericMeta(_GenericMeta):

        def __ne__(cls, other):
            # type: (object) -> bool
            is_equal = cls.__eq__(other)
            if is_equal is NotImplemented:
                return NotImplemented
            else:
                return not is_equal

else:
    GenericMeta = type  # type: ignore
