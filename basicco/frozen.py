"""Class decorator that can prevent modifying class and/or instance attributes."""

from typing import TYPE_CHECKING, overload

from .qualname import qualname

if TYPE_CHECKING:
    from typing import Callable, TypeVar, Optional, Literal

    FMT = TypeVar("FMT", bound="FrozenMeta")

__all__ = ["FROZEN_SLOT", "frozen", "FrozenMeta"]

_FROZEN_CLASS_TAG = "__isfrozenclass__"
_FROZEN_CLASS_INSTANCE_TAG = "__isfrozenclassinstance__"
_FROZEN_OBJECT_TAG = "__isfrozenobject__"

FROZEN_SLOT = "__isfrozeninstance__"
"""Required slot for freezing slotted object instances."""


@overload
def frozen(
    base,
    cls=None,
    obj=None,
):
    # type: (FMT, Literal[None], Literal[None]) -> FMT
    pass


@overload
def frozen(
    base=None,  # type: Literal[None]
    cls=None,  # type: Optional[bool]
    obj=None,  # type: Optional[bool]
):
    # type: (...) -> Callable[[FMT], FMT]
    pass


def frozen(base=None, cls=None, obj=None):
    """
    Class decorator that can prevent modifying class and/or instance attributes.

    :param base: Class to be decorated.

    :param cls: Whether to freeze class attributes.
    :type cls: bool or None

    :param obj: Whether to freeze instance attributes.
    :type obj: bool or None

    :return: Decorated class.
    """

    cls = True if cls is None else bool(cls)
    obj = True if obj is None else bool(obj)

    def decorator(_base):
        # type: (FMT) -> FMT

        if not isinstance(_base, FrozenMeta):
            error_ = "can't use 'frozen' decorator with non-{} class {}".format(
                FrozenMeta.__name__, repr(_base.__name__)
            )
            raise TypeError(error_)

        type.__setattr__(_base, _FROZEN_CLASS_TAG, cls)
        type.__setattr__(_base, _FROZEN_OBJECT_TAG, obj)

        if cls:
            type.__setattr__(_base, _FROZEN_CLASS_INSTANCE_TAG, True)

        if obj:
            super_setattr = _base.__dict__.get("__setattr__")
            super_delattr = _base.__dict__.get("__delattr__")

            def __setattr__(self, name, value):
                if (
                    getattr(type(self), _FROZEN_OBJECT_TAG)
                    and getattr(self, FROZEN_SLOT, False)
                ):
                    error = "instances of {} are frozen, can't set attribute".format(
                        repr(type(self).__name__)
                    )
                    raise AttributeError(error)
                elif super_setattr is not None:
                    super_setattr(_base, name, value)
                else:
                    super(_base, self).__setattr__(name, value)

            def __delattr__(self, name):
                if (
                    getattr(type(self), _FROZEN_OBJECT_TAG)
                    and getattr(self, FROZEN_SLOT, False)
                ):
                    error = "instances of {} are frozen, can't delete attribute".format(
                        repr(type(self).__name__)
                    )
                    raise AttributeError(error)
                elif super_delattr is not None:
                    super_delattr(_base, name)
                else:
                    super(_base, self).__delattr__(name)

            __setattr__.__module__ = __delattr__.__module__ = _base.__module__

            base_qualname = qualname(_base)
            __setattr__.__name__ = "__setattr__"
            __delattr__.__name__ = "__delattr__"
            __setattr__.__qualname__ = ".".join((base_qualname, "__setattr__"))
            __delattr__.__qualname__ = ".".join((base_qualname, "__delattr__"))

            type.__setattr__(_base, "__setattr__", __setattr__)
            type.__setattr__(_base, "__delattr__", __delattr__)

        return _base

    if base is None:
        return decorator
    else:
        return decorator(base)


class FrozenMeta(type):
    """Metaclass for classes that can be decorated with the 'frozen' decorator."""

    def __init__(cls, name, bases, dct):
        super(FrozenMeta, cls).__init__(name, bases, dct)
        type.__setattr__(
            cls, _FROZEN_CLASS_INSTANCE_TAG, getattr(cls, _FROZEN_CLASS_TAG, False)
        )

    def __call__(cls, *args, **kwargs):
        self = super(FrozenMeta, cls).__call__(*args, **kwargs)
        if getattr(cls, _FROZEN_OBJECT_TAG, False):
            if hasattr(self, "__dict__") or hasattr(cls, FROZEN_SLOT):
                if not getattr(self, FROZEN_SLOT, False):
                    object.__setattr__(self, FROZEN_SLOT, True)
            else:
                error = (
                    "could not freeze slotted instance of '{}.{}' since it doesn't "
                    "have a slot named {} (available as a constant at {}.{})"
                ).format(
                    cls.__module__,
                    qualname(cls),
                    repr(FROZEN_SLOT),
                    __name__,
                    "FROZEN_SLOT",
                )
                raise AttributeError(error)
        return self

    def __setattr__(cls, name, value):
        if (
            getattr(cls, _FROZEN_CLASS_TAG, False)
            and cls.__dict__.get(_FROZEN_CLASS_INSTANCE_TAG, False)
        ):
            error = "{} is frozen, can't set class attribute".format(
                repr(cls.__name__)
            )
            raise AttributeError(error)
        else:
            super(FrozenMeta, cls).__setattr__(name, value)

    def __delattr__(cls, name):
        if (
            getattr(cls, _FROZEN_CLASS_TAG, False)
            and cls.__dict__.get(_FROZEN_CLASS_INSTANCE_TAG, False)
        ):
            error = "{} is frozen, can't delete class attribute".format(
                repr(cls.__name__)
            )
            raise AttributeError(error)
        else:
            super(FrozenMeta, cls).__setattr__(name)
