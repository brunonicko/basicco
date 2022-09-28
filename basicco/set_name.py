"""Backport of the functionality of `__set_name__` from PEP 487 to Python 2.7."""

import sys

import six

__all__ = ["SetNameMeta", "SetName"]


class SetNameMeta(type):
    """Metaclass that backports the functionality of `__set_name__` from PEP 487 to Python 2.7."""

    if sys.version_info[:3] < (3, 6):

        @staticmethod
        def __new__(mcs, name, bases, dct, **kwargs):
            cls = super(SetNameMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            for member_name, member in six.iteritems(dct):
                if hasattr(member, "__set_name__") and not isinstance(member, type):
                    member.__set_name__(cls, member_name)
            return cls


class SetName(six.with_metaclass(SetNameMeta, object)):
    """Class that backports the functionality of `__set_name__` from PEP 487 to Python 2.7."""

    __slots__ = ()
