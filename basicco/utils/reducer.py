"""Python 2 compatible reducer method that works with qualified name and slots."""

from .import_path import get_import_path, import_from_path
from .slots import get_slots_state, set_slots_state

__all__ = ["reducer"]


def reducer(self):
    """Default reducer method that implements qualified name and slots for Python 2."""

    # Get import path to the class.
    cls = type(self)
    import_path = get_import_path(cls)

    # Return reducer with import path and state.
    if hasattr(self, "__dict__"):
        return _reducer, (import_path, self.__dict__)  # standard object
    else:
        return _slotted_reducer, (import_path, get_slots_state(self))  # slots


def _reducer(import_path, state):
    cls = import_from_path(import_path)
    self = cls.__new__(cls)
    self.__dict__.update(state)
    return self


def _slotted_reducer(import_path, slotted_state):
    cls = import_from_path(import_path)
    self = cls.__new__(cls)
    set_slots_state(self, slotted_state)
    return self
