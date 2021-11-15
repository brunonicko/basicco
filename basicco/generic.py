"""Improved compatibility with `typing.Generic` for Python 2.7."""

try:
    from typing import GenericMeta as _GenericMeta  # type: ignore
except ImportError:
    _GenericMeta = type

__all__ = ["GenericMeta"]


class GenericMeta(_GenericMeta):
    if _GenericMeta is not type:

        def __ne__(cls, other):
            # type: (object) -> bool
            return not super(GenericMeta, cls).__eq__(other)  # fix python 2 bug
