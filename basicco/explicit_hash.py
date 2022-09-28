"""Metaclass that forces `__hash__` to be declared when `__eq__` is declared."""

import six

__all__ = ["ExplicitHashMeta", "ExplicitHash"]


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
