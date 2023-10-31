"""Prevents changing public class attributes."""

import contextlib
import re

import six
from tippo import Any, Dict, Iterator, Tuple, Type, TypeVar, Union, cast

from basicco.mangling import mangle
from basicco.type_checking import assert_is_instance

__all__ = [
    "is_locked",
    "set_locked",
    "unlocked_context",
    "LockedClassMeta",
    "LockedClass",
]


def _locked_attr(cls_module, cls_name):
    # type: (str, str) -> str
    owner_name = "{}_{}".format(
        re.sub(r"\W|^(?=\d)", "_", cls_module).strip("_"),
        cls_name,
    )
    return mangle("__class_locked_", owner_name)


def is_locked(cls):
    # type: (Type[Any]) -> bool
    """
    Tell whether public attributes of a class are locked or not.

    :param cls: Class.
    :return: True if locked.
    """
    locked_attr = _locked_attr(cls.__original_module__, cls.__original_name__)  # noqa
    try:
        locked = cast(bool, getattr(cls, locked_attr))
    except AttributeError:
        assert_is_instance(cls, LockedClassMeta)
        return True
    else:
        return locked


def set_locked(cls, locked):
    # type: (Union[Type[LockedClass], LockedClassMeta], bool) -> None
    """
    Set class locked state.

    :param cls: Class.
    :param locked: Locked state.
    :raise TypeCheckError: Invalid class type.
    """
    locked_attr = _locked_attr(cls.__original_module__, cls.__original_name__)
    if not hasattr(cls, locked_attr):
        assert_is_instance(cls, LockedClassMeta)
    elif not locked:
        type.__setattr__(cls, locked_attr, False)
    else:
        type.__delattr__(cls, locked_attr)


@contextlib.contextmanager
def unlocked_context(cls):
    # type: (Union[Type[LockedClass], LockedClassMeta]) -> Iterator[None]
    """
    Unlocked class context manager.

    :param cls: Class.
    :raise TypeCheckError: Invalid class type.
    """
    before = is_locked(cls)
    if before:
        set_locked(cls, False)
    try:
        yield
    finally:
        if before:
            set_locked(cls, True)


class LockedClassMeta(type):
    """Metaclass that prevents changing public class attributes."""

    def __new__(
        mcs,  # type: Type[_LCM]
        name,  # type: str
        bases,  # type: Tuple[Type[Any], ...]
        dct,  # type: Dict[str, Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> _LCM
        dct = dict(dct)
        dct["__original_module__"] = dct.get("__module__", "no_module")
        dct["__original_name__"] = name
        dct[_locked_attr(dct["__original_module__"], dct["__original_name__"])] = False
        return super(LockedClassMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)

    def __init__(cls, name, bases, dct, **kwargs):
        # type: (str, Tuple[Type[Any], ...], Dict[str, Any], **Any) -> None
        super(LockedClassMeta, cls).__init__(name, bases, dct, **kwargs)
        if not is_locked(cls):
            set_locked(cls, True)

    def __getattr__(cls, name):
        # type: (str) -> Any
        if name == _locked_attr(cls.__original_module__, cls.__original_name__):
            return True
        try:
            return super(LockedClassMeta, cls).__getattr__(name)  # type: ignore  # noqa
        except AttributeError:
            pass
        error = "class {!r} has no attribute {!r}".format(cls.__name__, name)
        raise AttributeError(error)

    def __setattr__(cls, name, value):
        # type: (str, Any) -> None
        """Prevent setting public class attributes."""
        if is_locked(cls) and not name.startswith("_"):
            error = "can't set read-only class attribute {!r}".format(name)
            raise AttributeError(error)
        super(LockedClassMeta, cls).__setattr__(name, value)

    def __delattr__(cls, name):
        # type: (str) -> None
        """Prevent deleting class attributes."""
        if is_locked(cls) and not name.startswith("_"):
            error = "can't delete read-only class attribute {!r}".format(name)
            raise AttributeError(error)
        super(LockedClassMeta, cls).__delattr__(name)


_LCM = TypeVar("_LCM", bound=LockedClassMeta)


class LockedClass(six.with_metaclass(LockedClassMeta, object)):
    """Class that prevents changing public class attributes."""

    __slots__ = ()
