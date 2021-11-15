"""Utility functions for managing object state."""

import inspect
from types import MemberDescriptorType
from typing import TYPE_CHECKING

from six import iteritems

if TYPE_CHECKING:
    from typing import Any, Dict, Set, Mapping

__all__ = ["get_state", "update_state"]


def get_state(obj):
    # type: (Any) -> Dict[str, Any]
    """
    Get dictionary with an object's attribute values.
    Works with regular and slotted objects.

    .. code:: python

        >>> from basicco.utils.state import get_state, update_state
        >>> class SlottedObject(object):
        ...     __slots__ = ("a", "b")
        ...     def __init__(self, a, b):
        ...         self.a = a
        ...         self.b = b
        ...
        >>> slotted_obj = SlottedObject(1, 2)
        >>> obj_state = get_state(slotted_obj)
        >>> obj_state["a"], obj_state["b"]
        (1, 2)

    :param obj: Object instance or class.
    :type obj: object or type

    :return: State dictionary.
    :rtype: dict[str, Any]

    :raises TypeError: Provided object has no state.
    """
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    if not hasattr(type(obj), "__slots__"):
        error = "{} object has no state".format(repr(type(obj).__name__))
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


def update_state(obj, state_update):
    # type: (Any, Mapping[str, Any]) -> None
    """
    Update attribute values for an object.
    Works with regular and slotted objects.

    .. code:: python

        >>> from basicco.utils.state import get_state, update_state
        >>> class SlottedObject(object):
        ...     __slots__ = ("a", "b")
        ...     def __init__(self, a, b):
        ...         self.a = a
        ...         self.b = b
        ...
        >>> slotted_object = SlottedObject(1, 2)
        >>> update_state(slotted_object, {"a": 3, "b": 4})
        >>> slotted_object.a, slotted_object.b
        (3, 4)

    :param obj: Object instance or class.
    :type obj: object or type

    :param state_update: Dictionary with state updates.
    :type state_update: dict[str, Any]

    :raises TypeError: Provided object has no state.
    """
    if hasattr(obj, "__dict__"):
        if isinstance(obj, type):
            for attribute, value in iteritems(state_update):
                type.__setattr__(obj, attribute, value)
        else:
            obj.__dict__.update(state_update)
        return
    if not hasattr(type(obj), "__slots__"):
        error = "{} object has no state".format(repr(type(obj).__name__))
        raise TypeError(error)

    remaining = set(state_update)  # type: Set[str]
    cls = type(obj)
    for base in inspect.getmro(cls):
        if base is object:
            continue

        for slot, value in iteritems(state_update):

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

            # Set value using the member descriptor.
            member.__set__(obj, state_update[slot])
            remaining.remove(slot)

        if not remaining:
            return

    if remaining:
        error = "could not find slot(s) {} in {}".format(
            ", ".join("'{}'".format(s) for s in sorted(remaining)), repr(cls.__name__)
        )
        raise AttributeError(error)
