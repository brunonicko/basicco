"""Backport of the functionality of `__set_name__` from PEP 487 to Python 2.7."""

import sys

import six
from tippo import Any, Dict, Tuple, Type, TypeVar

__all__ = ["SetNameMeta", "SetName"]


class SetNameMeta(type):
    """Backports the functionality of `__set_name__` from PEP 487."""

    if sys.version_info[:3] < (3, 6):

        @staticmethod
        def __new__(
            mcs,  # type: Type[_SNM]
            name,  # type: str
            bases,  # type: Tuple[Type[Any], ...]
            dct,  # type: Dict[str, Any]
            **kwargs  # type: Any
        ):
            # type: (...) -> _SNM
            cls = super(SetNameMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            for member_name, member in six.iteritems(dct):
                if hasattr(member, "__set_name__") and not isinstance(member, type):
                    member.__set_name__(cls, member_name)
            return cls


_SNM = TypeVar("_SNM", bound=SetNameMeta)


class SetName(six.with_metaclass(SetNameMeta, object)):
    """Backports the functionality of `__set_name__` from PEP 487."""

    __slots__ = ()
