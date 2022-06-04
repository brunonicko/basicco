"""Decorator that prevents an abstract class from being instantiated."""

import functools
from typing import Type, TypeVar

__all__ = ["abstract_class"]


_T = TypeVar("_T")
_ABSTRACT_CLASS = "__abstract_class__"


def abstract_class(cls: Type[_T]) -> Type[_T]:
    """
    Decorates a class as abstract.
    This decorator should be used at the top of the decorator stack.

    :param cls: Class.
    :return: Decorated class.
    """

    # Tag this class as abstract.
    type.__setattr__(cls, _ABSTRACT_CLASS, cls)

    # Get original new method.
    original_new = cls.__dict__.get("__new__")
    if isinstance(original_new, staticmethod):
        original_new = original_new.__func__

    # Replace it with one that checks for abstraction.
    @functools.wraps(original_new or object.__new__)
    def __new__(cls_, *args, **kwargs):
        if type.__getattribute__(cls_, _ABSTRACT_CLASS) is cls_:
            raise NotImplementedError(f"can't instantiate abstract class {cls_.__qualname__!r}")
        elif original_new is not None:
            return original_new(cls_, *args, **kwargs)
        else:
            return super(cls, cls_).__new__(cls_, *args, **kwargs)  # type: ignore

    type.__setattr__(cls, "__new__", staticmethod(__new__))

    return cls
