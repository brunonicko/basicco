"""Utility functions for managing slots."""

import inspect
from types import MemberDescriptorType
from typing import TYPE_CHECKING

from six import iteritems

if TYPE_CHECKING:
    from typing import Any, Dict, Set

__all__ = ["get_slots_state", "set_slots_state"]


def get_slots_state(obj):
    # type: (Any) -> Dict[str, Any]
    """
    Get a dictionary with values associated to an object's slots.

    :param obj: Slotted object.
    :type obj: object

    :return: Slots state dictionary.
    :rtype: dict[str, Any]

    :raises TypeError: Provided non-slotted object.
    """
    if hasattr(obj, "__dict__") or not hasattr(type(obj), "__slots__"):
        error = "provided non-slotted {} object".format(type(obj).__name__)
        raise TypeError(error)

    state = {}  # type: Dict[str, Any]
    cls = type(obj)
    for base in inspect.getmro(cls):
        if base is object:
            continue

        for slot in base.__slots__:

            # Skip weak reference slot.
            if slot == "__weakref__":
                continue

            # Privatize slot if needed.
            if slot.startswith("__") and not slot.endswith("__"):
                slot = "_{}{}".format(cls.__name__.lstrip("_"), slot)

            # Skip if already has a value.
            if slot in state:
                continue

            # Try to get value using the member descriptor.
            try:
                state[slot] = base.__dict__[slot].__get__(obj, cls)
            except (KeyError, AttributeError):
                pass

    return state


def set_slots_state(obj, state):
    # type: (Any, Dict[str, Any]) -> None
    """
    Set the values for the slots in an object.

    :param obj: Slotted object.
    :type obj: object

    :param state: Slots state dictionary.
    :type state: dict[str, Any]

    :raises TypeError: Provided non-slotted object.
    :raises AttributeError: Object doesn't have slot.
    """
    if hasattr(obj, "__dict__") or not hasattr(type(obj), "__slots__"):
        error = "provided non-slotted {} object".format(type(obj).__name__)
        raise TypeError(error)

    remaining = set(state)  # type: Set[str]
    cls = type(obj)
    for base in inspect.getmro(cls):
        if base is object:
            continue

        for slot, value in iteritems(state):

            # Skip if already set.
            if slot not in remaining:
                continue

            # Skip slot if not in this base.
            if slot not in base.__dict__:
                continue

            # Get member.
            member = base.__dict__[slot]
            if not isinstance(member, MemberDescriptorType):
                error = "'{}.{}' is not a slot".format(cls.__name__, slot)
                raise AttributeError(error)

            # Set value and pop it from the state.
            member.__set__(obj, state[slot])
            remaining.remove(slot)

        if not remaining:
            return

    if remaining:
        error = "could not find slot(s) {} in {}".format(
            ", ".join("'{}'".format(s) for s in sorted(remaining)), repr(cls.__name__)
        )
        raise AttributeError(error)
