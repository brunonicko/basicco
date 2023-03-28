"""
Metaclass that forces `__hash__` to None when `__eq__` is declared.
This is a backport of the default behavior in
`Python 3 <https://docs.python.org/3/reference/datamodel.html#object.__hash__>`_.
"""

import six
from tippo import Any, Dict, Tuple, Type, TypeVar

__all__ = ["ImplicitHashMeta", "ImplicitHash"]


class ImplicitHashMeta(type):
    """Metaclass that forces `__hash__` to None when `__eq__` is declared."""

    def __new__(
        mcs,  # type: Type[_IHM]
        name,  # type: str
        bases,  # type: Tuple[Type[Any], ...]
        dct,  # type: Dict[str, Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> _IHM
        if "__eq__" in dct and "__hash__" not in dct:
            dct = dict(dct)
            dct["__hash__"] = None
        return super(ImplicitHashMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)


_IHM = TypeVar("_IHM", bound=ImplicitHashMeta)


class ImplicitHash(six.with_metaclass(ImplicitHashMeta, object)):
    """Class that forces `__hash__` to None when `__eq__` is declared."""

    __slots__ = ()
