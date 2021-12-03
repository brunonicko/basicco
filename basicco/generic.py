"""Improved compatibility with `typing.Generic` for Python 2.7."""

from .utils.generic_meta import GenericMeta as _GenericMeta

__all__ = ["GenericMeta"]


class GenericMeta(_GenericMeta):
    pass
