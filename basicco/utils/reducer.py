"""Python 2.7 compatible reducer method that works with qualified name and slots."""

from .import_path import get_import_path, import_from_path
from .state import get_state, update_state

__all__ = ["reducer"]


def reducer(self):
    """
    Default reducer method that implements qualified name and slots for Python 2.7.
    """
    return _reducer, (get_import_path(type(self)), get_state(self))


def _reducer(import_path, state):
    cls = import_from_path(import_path)
    self = cls.__new__(cls)
    update_state(self, state)
    return self
