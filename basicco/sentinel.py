"""Sentinel value utilities."""

import six
from tippo import Any, Dict, NoReturn, Tuple, Type, TypeVar, Union, cast

__all__ = ["SentinelType"]


class SentinelMeta(type):
    """Sentinel metaclass."""

    __instance__ = None  # type: Union[SentinelType, None]

    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):
        # type: (Type[_SM], str, Tuple[Type[Any], ...], Dict[str, Any], **Any) -> _SM
        dct = dict(dct, __slots__=())
        try:
            _ = SentinelType
        except NameError:
            dct["__new__"] = staticmethod(_abstract_new)
        else:
            if bases != (SentinelType,):
                error = "can only inherit directly from {!r}".format(
                    SentinelType.__name__
                )
                raise TypeError(error)
            dct["__new__"] = staticmethod(_sentinel_new)
        cls = super(SentinelMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
        cls.__instance__ = object.__new__(cast(Type["SentinelType"], cls))
        return cls


_SM = TypeVar("_SM", bound=SentinelMeta)


def _abstract_new(cls, *args, **kwargs):  # noqa
    # type: (SentinelMeta, *Any, **Any) -> NoReturn
    error = "can't instantiate abstract class {!r}".format(cls.__name__)
    raise NotImplementedError(error)


def _sentinel_new(cls, *args, **kwargs):  # noqa
    # type: (Type[SentinelType], *Any, **Any) -> SentinelType
    assert cls.__instance__ is not None
    return cls.__instance__


class SentinelType(six.with_metaclass(SentinelMeta, object)):
    """Sentinel type."""

    __slots__ = ()
