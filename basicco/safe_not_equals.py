"""
Backport of the default Python 3 behavior of `__ne__` behavior for Python 2.7.
`Read more <https://docs.python.org/3.0/whatsnew/3.0.html#operators-and-special-methods>`_.
"""

import functools
import sys

import six

from .dynamic_code import generate_unique_filename, make_function

__all__ = ["SafeNotEqualsMeta", "SafeNotEquals"]


class SafeNotEqualsMeta(type):
    """Metaclass that backports the default Python 3 behavior of `__ne__` behavior for Python 2.7."""

    if sys.version_info[:1] < (3,):

        @staticmethod
        def __new__(mcs, name, bases, dct, **kwargs):
            cls = super(SafeNotEqualsMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            if cls.__ne__ is object.__ne__:
                script = "def __ne__(self, other):\n    return not (self == other)"
                func_name = "__ne__"
                module = dct.get("__module__", None)
                func = make_function(
                    name=func_name,
                    script=script,
                    globs={},
                    filename=generate_unique_filename(func_name, module=module, owner_name=name),
                    module=module,
                )
                func = functools.wraps(object.__ne__)(func)
                type.__setattr__(cls, func_name, func)
            return cls


class SafeNotEquals(six.with_metaclass(SafeNotEqualsMeta, object)):
    """Class that backports the default Python 3 behavior of `__ne__` behavior for Python 2.7."""

    __slots__ = ()
