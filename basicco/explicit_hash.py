"""Forces `__hash__` to be declared when `__eq__` is declared."""

import six
from tippo import Any, Callable, Dict, Tuple, Type, TypeVar, cast

__all__ = ["ExplicitHashMeta", "ExplicitHash", "set_to_none"]


_T = TypeVar("_T")


class ExplicitHashMeta(type):
    """Forces `__hash__` to be declared when `__eq__` is declared."""

    @staticmethod
    def __new__(
        mcs,  # type: Type[_EHM]
        name,  # type: str
        bases,  # type: Tuple[Type[Any], ...]
        dct,  # type: Dict[str, Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> _EHM
        if "__eq__" in dct and "__hash__" not in dct:
            error = "declared '__eq__' in {!r} but didn't declare '__hash__'".format(
                name
            )
            raise TypeError(error)
        return super(ExplicitHashMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)


_EHM = TypeVar("_EHM", bound=ExplicitHashMeta)


class ExplicitHash(six.with_metaclass(ExplicitHashMeta, object)):
    """Forces `__hash__` to be declared when `__eq__` is declared."""

    __slots__ = ()


def set_to_none(_hash_method):
    # type: (Callable[[_T], int]) -> Callable[[_T], int]
    """
    Decorates a '__hash__' method, so it gets set to None for non-hashable classes.

    :param _hash_method: Hash method function.
    :return: None
    """
    return cast(Callable[[_T], int], None)
