"""Utility functions for managing object state."""

import sys
import types

import six
from tippo import Any, Callable, Mapping, Type

from .dynamic_code import generate_unique_filename, make_function
from .get_mro import get_mro
from .import_path import get_path, import_path
from .mangling import mangle

__all__ = ["get_state", "update_state", "reducer", "ReducibleMeta", "Reducible"]


def get_state(obj):
    # type: (Any) -> dict[str, Any]
    """
    Get dictionary with an object's attribute values.
    Works with regular and slotted objects.

    :param obj: Object instance or class.
    :return: State dictionary.
    """
    state = {}  # type: dict[str, Any]

    # Get slotted values.
    if not isinstance(obj, type) and hasattr(type(obj), "__slots__"):
        cls = type(obj)
        for base in get_mro(cls):

            # Skip object.
            if base is object:
                continue

            # Get slot values.
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

    # Get normal values.
    if hasattr(obj, "__dict__"):
        state.update(dict(obj.__dict__))

    return state


def update_state(obj, state_update):
    # type: (Any, Mapping[str, Any]) -> None
    """
    Update attribute values for an object.
    Works with regular and slotted objects.

    :param obj: Object instance or class.
    :param state_update: Dictionary with state updates.
    """
    remaining = set(state_update)  # type: set[str]

    # Set slotted attributes.
    if not isinstance(obj, type) and hasattr(type(obj), "__slots__"):
        cls = type(obj)
        for base in get_mro(cls):

            # Nothing left to do.
            if not remaining:
                return

            # Skip object.
            if base is object:
                continue

            # Set slot values.
            for slot in tuple(remaining):

                # Skip if not a slot in this base.
                member = base.__dict__.get(slot)
                if not isinstance(member, types.MemberDescriptorType):
                    continue

                # Set value using the member descriptor.
                member.__set__(obj, state_update[slot])
                remaining.remove(slot)

    # Set remaining attributes normally.
    for name in remaining:
        if isinstance(obj, type):
            type.__setattr__(obj, name, state_update[name])
        else:
            object.__setattr__(obj, name, state_update[name])


def _reducer(cls_or_path, state):
    if isinstance(cls_or_path, six.string_types):
        cls = import_path(cls_or_path)
    else:
        cls = cls_or_path
    self = cls.__new__(cls)
    update_state(self, state)
    return self


def _make_reducer(name, owner=None):
    # type: (str, Type | None) -> Callable
    script = """def {}(self):
    \"\"\"Reducer method that supports qualified name and slots for Python 2.7.\"\"\"
    cls = type(self)
    try:
        cls_or_path = get_path(cls)
    except ImportError:
        cls_or_path = cls
    return _reducer, (cls_or_path, get_state(self))
""".format(
        name
    )
    if owner is None:
        module = __name__
        owner_name = None
    else:
        module = owner.__module__
        owner_name = owner.__name__
    return make_function(
        name,
        script,
        globs={"get_path": get_path, "_reducer": _reducer, "get_state": get_state},
        filename=generate_unique_filename(name, module=module, owner_name=owner_name),
        module=module,
    )


reducer = _make_reducer("reducer")


class ReducibleMeta(type):
    """Metaclass that allows slotted classes to be pickled in Python 2.7."""

    if sys.version_info[0:2] < (3, 4):

        @staticmethod
        def __new__(mcs, name, bases, dct, **kwargs):
            cls = super(ReducibleMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            old_reducer = getattr(cls, "__reduce__", None)
            if old_reducer is None or old_reducer is object.__reduce__:
                type.__setattr__(cls, "__reduce__", _make_reducer("__reducer__", cls))
            return cls


class Reducible(six.with_metaclass(ReducibleMeta, object)):
    """
    Class that allows slotted classes to be pickled in Python 2.7.
    See `PEP 307 <https://peps.python.org/pep-0307/>`_.
    """

    __slots__ = ()
