"""
Metaclass that forces `__hash__` to None when `__eq__` is declared.
This is a backport of the default behavior in
`Python 3 <https://docs.python.org/3/reference/datamodel.html#object.__hash__>`_.
"""

import six

__all__ = ["ImplicitHashMeta", "ImplicitHash"]


class ImplicitHashMeta(type):
    """Metaclass that forces `__hash__` to None when `__eq__` is declared."""

    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):
        if "__eq__" in dct and "__hash__" not in dct:
            dct = dict(dct)
            dct["__hash__"] = None
        return super(ImplicitHashMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)


class ImplicitHash(six.with_metaclass(ImplicitHashMeta, object)):
    """Class that forces `__hash__` to None when `__eq__` is declared."""

    __slots__ = ()
