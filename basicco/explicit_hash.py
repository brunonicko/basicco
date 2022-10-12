"""Metaclass that forces `__hash__` to be declared when `__eq__` is declared."""

import six
from tippo import Callable, TypeVar, cast

__all__ = ["ExplicitHashMeta", "ExplicitHash", "set_to_none"]


T = TypeVar("T")


class ExplicitHashMeta(type):
    """Metaclass that forces `__hash__` to be declared when `__eq__` is declared."""

    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):
        if "__eq__" in dct and "__hash__" not in dct:
            error = "declared '__eq__' in {!r} but didn't declare '__hash__'".format(name)
            raise TypeError(error)
        return super(ExplicitHashMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)


class ExplicitHash(six.with_metaclass(ExplicitHashMeta, object)):
    """Class that forces `__hash__` to be declared when `__eq__` is declared."""

    __slots__ = ()


def set_to_none(_hash_method):
    # type: (Callable[[T], int]) -> Callable[[T], int]
    """
    Decorates a '__hash__' method, so it gets set to None for non-hashable classes.

    :param _hash_method: Hash method function.
    :return: None
    """
    return cast(Callable[[T], int], None)
