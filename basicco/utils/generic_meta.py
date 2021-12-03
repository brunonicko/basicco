"""Improved compatibility with `typing.Generic` for Python 2.7."""

try:
    from typing import GenericMeta as _GenericMeta  # type: ignore
except ImportError:
    _GenericMeta = type

__all__ = ["GenericMeta"]


if _GenericMeta is type:
    GenericMeta = type
else:
    class GenericMeta(_GenericMeta):

        def __ne__(cls, other):
            # type: (object) -> bool
            return not super(GenericMeta, cls).__eq__(other)  # fix python 2 bug
