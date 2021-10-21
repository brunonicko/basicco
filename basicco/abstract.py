"""Matches Python 2 behavior with Python 3 for abstract members."""

import inspect
from abc import ABCMeta
from typing import TYPE_CHECKING

from six import iteritems

if TYPE_CHECKING:
    from typing import Set

__all__ = ["AbstractMeta"]

_ABSTRACT_METHOD_TAG = "__isabstractmethod__"
_ABSTRACT_METHODS = "__abstractmethods__"


class AbstractMeta(ABCMeta):
    """Finds abstract members in properties and descriptors for both Python 2 and 3."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(AbstractMeta, cls).__init__(name, bases, dct, **kwargs)

        # Iterate over MRO of the class.
        abstract_method_names = set(
            getattr(cls, _ABSTRACT_METHODS, ())
        )  # type: Set[str]
        for base in reversed(inspect.getmro(cls)):

            # Find abstract members.
            for member_name, member in iteritems(base.__dict__):
                is_abstract = False

                # Descriptor.
                if hasattr(member, "__get__"):
                    is_abstract |= getattr(member, _ABSTRACT_METHOD_TAG, False)

                    # Has 'fget' getter (property-like).
                    if hasattr(member, "fget"):
                        is_abstract |= getattr(member.fget, _ABSTRACT_METHOD_TAG, False)

                # Static or class method.
                if isinstance(member, (staticmethod, classmethod)):
                    is_abstract |= getattr(member.__func__, _ABSTRACT_METHOD_TAG, False)

                # Regular method.
                if callable(member):
                    is_abstract |= getattr(member, _ABSTRACT_METHOD_TAG, False)

                # Keep track.
                if is_abstract:
                    abstract_method_names.add(member_name)

            # Update class information.
            type.__setattr__(cls, _ABSTRACT_METHODS, frozenset(abstract_method_names))
