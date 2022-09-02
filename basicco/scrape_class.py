"""Scrape class for members."""

from __future__ import absolute_import, division, print_function

import six
from tippo import TYPE_CHECKING, Protocol

from .get_mro import get_mro

if TYPE_CHECKING:
    from tippo import Any, Dict, Type

__all__ = [
    "BASE_OBJECT_MEMBER_NAMES",
    "DEFAULT_MEMBER_FILTER",
    "ALL_MEMBERS_FILTER",
    "MemberFilterProtocol",
    "OverrideFilterProtocol",
    "MemberReplacerProtocol",
    "scrape_class",
]


BASE_OBJECT_MEMBER_NAMES = frozenset(object.__dict__).union({"__dict__", "__module__", "__weakref__"})
DEFAULT_MEMBER_FILTER = lambda b, mn, m: mn not in BASE_OBJECT_MEMBER_NAMES
ALL_MEMBERS_FILTER = lambda b, mn, m: True


class MemberFilterProtocol(Protocol):
    def __call__(self, base, member_name, member):
        # type: (Type, str, Any) -> bool
        pass


class OverrideFilterProtocol(Protocol):
    def __call__(self, base, member_name, member, previous_member):
        # type: (Type, str, Any, Any) -> bool
        pass


class MemberReplacerProtocol(Protocol):
    def __call__(self, base, member_name, member):
        # type: (Type, str, Any) -> Any
        pass


def scrape_class(cls, member_filter=DEFAULT_MEMBER_FILTER, override_filter=None, member_replacer=None):
    # type: (Type, MemberFilterProtocol, OverrideFilterProtocol | None, MemberReplacerProtocol | None) -> Dict[str, Any]
    """
    Scrape class for specific members.

    :param cls: Class.
    :param member_filter: Member filter function.
    :param override_filter: Member override filter function.
    :param member_replacer: Member replacer function.
    :return: Dictionary with filtered members mapped by name.
    """
    if override_filter is None:
        override_filter = lambda b, mn, m, pm: member_filter(b, mn, m)

    members = {}  # type: Dict[str, Any]
    for base in reversed(get_mro(cls)):
        for member_name, member in six.iteritems(base.__dict__):
            override = member_name in members
            if (override and override_filter(base, member_name, member, members[member_name])) or (
                not override and member_filter(base, member_name, member)
            ):
                if member_replacer is not None:
                    member = member_replacer(base, member_name, member)
                members[member_name] = member
            elif override:
                del members[member_name]

    return members
