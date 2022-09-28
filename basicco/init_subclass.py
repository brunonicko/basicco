"""
Backport of the functionality of `__init_subclass__` from
`PEP 487 <https://peps.python.org/pep-0487/>`_ to Python 2.7.
"""

import sys

import six

from .get_mro import get_mro

__all__ = ["InitSubclassMeta", "InitSubclass"]


class InitSubclassMeta(type):
    """Metaclass that backports the functionality of `__init_subclass__` from PEP 487 to Python 2.7."""

    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):

        # Keep a copy of the original kwargs -- they are sometimes used by generics.
        original_kwargs = dict(kwargs)

        # Wipe out kwargs if using older python.
        if sys.version_info[:3] < (3, 6):
            kwargs = dict()

        # Get compatibility kwargs (defined in the body of the class).
        dct_had_kwargs = "__kwargs__" in dct
        if dct_had_kwargs:
            compat_kwargs = dct["__kwargs__"]
        else:
            compat_kwargs = {}

        # Error out if the same kwarg is defined both in the body and in the class arguments.
        conflicting_kwargs = set(compat_kwargs).intersection(kwargs)
        if conflicting_kwargs:
            error = "conflicting class keyword arguments {}".format(
                ", ".join(sorted(repr(k) for k in conflicting_kwargs))
            )
            raise TypeError(error)

        # Merge kwargs.
        kwargs.update(compat_kwargs)

        # For older python versions.
        if sys.version_info[:3] < (3, 6):

            # Ensure classmethod.
            if "__init_subclass__" in dct and not isinstance(dct["__init_subclass__"], classmethod):
                dct = dict(dct)
                dct["__init_subclass__"] = classmethod(dct["__init_subclass__"])

            # Build class and pass original kwargs (for generics).
            cls = super(InitSubclassMeta, mcs).__new__(mcs, name, bases, dct, **original_kwargs)

            # Find '__init_subclass__' method.
            method = None
            method_owner = None
            for base in get_mro(cls):
                if base is cls:
                    continue
                method = base.__dict__.get("__init_subclass__")
                if method is not None:
                    method_owner = base
                    break

            # Found a method.
            if method is not None:

                # Invalid base.
                if not isinstance(method_owner, InitSubclassMeta):
                    error = "base {!r} defines '__init_subclass__' but does not utilize {!r} as a metaclass".format(
                        method_owner.__name__, InitSubclassMeta.__name__
                    )
                    raise TypeError(error)

                # Call it with compat kwargs only.
                method.__func__(cls, **compat_kwargs)

            # Have kwargs but no method was found.
            elif kwargs:
                error = "object.__init_subclass__() takes no keyword arguments"
                raise TypeError(error)

        # We don't need to do anything for newer python versions, just pass the merged kwargs.
        else:
            cls = super(InitSubclassMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)

        # Remove kwargs from the body of the class.
        if not dct_had_kwargs and hasattr(cls, "__kwargs__"):
            error = "one or more bases for class {!r} define {!r} but do not utilize {!r} as a metaclass".format(
                name, "__kwargs__", InitSubclassMeta.__name__
            )
            raise TypeError(error)
        elif dct_had_kwargs:
            type.__delattr__(cls, "__kwargs__")

        return cls


class InitSubclass(six.with_metaclass(InitSubclassMeta, object)):
    """Class that backports the functionality of `__init_subclass__` from PEP 487 to Python 2.7"""

    __slots__ = ()

    if sys.version_info[:3] < (3, 6):

        def __init_subclass__(cls):
            pass
