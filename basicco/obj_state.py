"""Utility functions for managing object state."""

import inspect
import sys
import types

import six
from tippo import Any, Mapping

from .import_path import get_path, import_path
from .mangling import mangle

__all__ = ["get_state", "update_state", "reducer", "ReducibleMeta", "Reducible"]


def get_state(obj):  # FIXME: test mixed classes (slotted and non-slotted)
    # type: (Any) -> dict[str, Any]
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
        error = "{!r} object has no state".format(type(obj).__name__)
        raise TypeError(error)

    state = {}  # type: dict[str, Any]
    cls = type(obj)
    for base in inspect.getmro(cls):
        if base is object:
            continue

        for slot in getattr(base, "__slots__", ()):

            # Skip weak reference slot.
            if slot == "__weakref__":
                continue

            # Mangle slot if needed.
            slot = mangle(slot, base.__name__)

            # Skip if already has a value.
            if slot in state:
                continue

            # Try to get value using the member descriptor.
            try:
                state[slot] = base.__dict__[slot].__get__(obj, cls)
            except (KeyError, AttributeError):
                pass

    return state


def update_state(obj, state_update):  # FIXME: test mixed classes (slotted and non-slotted)
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
        error = "{!r} object has no state".format(type(obj).__name__)
        raise TypeError(error)

    remaining = set(state_update)  # type: set[str]
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
        error = "could not find slot(s) {} in {!r}".format(", ".join(repr(s) for s in sorted(remaining)), cls.__name__)
        raise AttributeError(error)


def _reducer(cls_or_path, state):
    if isinstance(cls_or_path, six.string_types):
        cls = import_path(cls_or_path)
    else:
        cls = cls_or_path
    self = cls.__new__(cls)
    update_state(self, state)
    return self


def reducer(self):
    """Reducer method that supports qualified name and slots for Python 2.7."""
    cls = type(self)
    try:
        cls_or_path = get_path(cls)
    except ImportError:
        cls_or_path = cls
    return _reducer, (cls_or_path, get_state(self))


class ReducibleMeta(type):
    """Metaclass that allows slotted classes to be pickled in Python 2.7."""

    if sys.version_info[0:2] < (3, 4):

        @staticmethod
        def __new__(mcs, name, bases, dct, **kwargs):
            cls = super(ReducibleMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            old_reducer = getattr(cls, "__reduce__", None)
            if old_reducer is None or old_reducer is object.__reduce__:
                type.__setattr__(cls, "__reduce__", reducer)
            return cls


class Reducible(six.with_metaclass(ReducibleMeta, object)):
    """
    Class that allows slotted classes to be pickled in Python 2.7.
    See `PEP 307 <https://peps.python.org/pep-0307/>`_.
    """

    __slots__ = ()
