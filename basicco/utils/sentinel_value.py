from typing import TYPE_CHECKING

from .caller_module import get_caller_module
from .import_path import import_from_path

if TYPE_CHECKING:
    from typing import Tuple, Optional

__all__ = ["sentinel_value"]


def _sentinel_reducer(path):
    return import_from_path(path, None, ())()


def sentinel_value(
    name,  # type: str
    representation=None,  # type: Optional[str]
    module=None,  # type: Optional[str]
    boolean=False,  # type: bool
    type_name=None,  # type: Optional[str]
):
    # type: (...) -> Tuple[type, object]
    """
    Create unique sentinel type and object.

    .. code:: python

        >>> from basicco.utils.sentinel_value import sentinel_value
        >>> NothingType, Nothing = sentinel_value("Nothing")

    :param name: Name.
    :param representation: Representation string (or None to match name).
    :param module: Module name (or None to use caller's module).
    :param boolean: Boolean cast value (default is False).
    :param type_name: Type name (or None for automatic).
    :return: Sentinel type and object.
    """
    if module is None:
        module = get_caller_module()
    if type_name is None:
        type_name = "{}Type".format(name)

    def __new__(cls):
        try:
            self = cls.__instance__
        except AttributeError:
            self = cls.__instance__ = object.__new__(cls)
        return self

    def __repr__(_, _representation=representation or name):
        return _representation

    def __bool__(_, _boolean=bool(boolean)):
        return _boolean

    def __hash__(self):
        return object.__hash__(self)

    def __eq__(self, other):
        return other is self

    def __reduce__(self):
        cls = type(self)
        path = "|".join((cls.__module__, cls.__name__))
        return _sentinel_reducer, (path,)

    dct = {
        "__slots__": (),
        "__module__": module,
        "__new__": staticmethod(__new__),
        "__repr__": __repr__,
        "__bool__": __bool__,
        "__nonzero__": __bool__,
        "__hash__": __hash__,
        "__eq__": __eq__,
        "__reduce__": __reduce__,
    }
    sentinel_type = type(type_name, (object,), dct)
    sentinel_instance = sentinel_type()
    return sentinel_type, sentinel_instance
