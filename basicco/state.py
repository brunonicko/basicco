"""Utility functions for managing object state."""

import inspect
import types

from tippo import Any, Dict, Set, Mapping
import six

from .import_path import get_path, import_path

__all__ = ["get_state", "update_state", "reducer"]


def get_state(obj):
    # type: (Any) -> Dict[str, Any]
    """
    Get dictionary with an object's attribute values.
    Works with regular and slotted objects.

    :param obj: Object instance or class.
    :return: State dictionary.
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

        for slot in getattr(base, "__slots__", ()):

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

    :param obj: Object instance or class.
    :param state_update: Dictionary with state updates.
    :raises TypeError: Provided object has no state.
    """
    if hasattr(obj, "__dict__"):
        if isinstance(obj, type):
            for attribute, value in six.iteritems(state_update):
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

        for slot, value in six.iteritems(state_update):

            # Skip if already set.
            if slot not in remaining:
                continue

            # Skip slot if not in this base.
            if slot not in base.__dict__:
                continue

            # Get member.
            member = base.__dict__[slot]
            if not isinstance(member, types.MemberDescriptorType):
                error = "'{}.{}' is not a slot".format(cls.__name__, slot)
                raise AttributeError(error)

            # Set value using the member descriptor.
            member.__set__(obj, state_update[slot])
            remaining.remove(slot)

        if not remaining:
            return

    if remaining:
        error = "could not find slot(s) {} in {}".format(
            ", ".join(repr(s) for s in sorted(remaining)), repr(cls.__name__)
        )
        raise AttributeError(error)


def _reducer(path, state):
    cls = import_path(path)
    self = cls.__new__(cls)
    update_state(self, state)
    return self


def reducer(self):
    """Reducer method that supports qualified name and slots for Python 2.7."""
    return _reducer, (get_path(type(self)), get_state(self))
