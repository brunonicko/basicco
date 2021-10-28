"""Class decorator that can prevent modifying class and/or instance attributes."""

from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import Callable, TypeVar, Optional, Literal

    FMT = TypeVar("FMT", bound="FrozenMeta")

__all__ = ["FROZEN_SLOT", "freeze", "frozen", "FrozenMeta"]

_FROZEN_DECORATED_TAG = "__isfrozendecoratedclass__"
_FROZEN_CLASS_TAG = "__isfrozenclass__"
_FROZEN_CLASS_INSTANCE_TAG = "__isfrozenclassinstance__"
_FROZEN_OBJECT_TAG = "__isfrozenobject__"

FROZEN_SLOT = "__isfrozeninstance__"
"""Required slot for freezing slotted object instances."""


@overload
def frozen(cls, classes=None, instances=None):
    # type: (FMT, Optional[bool], Optional[bool]) -> FMT
    pass


@overload
def frozen(cls=None, classes=None, instances=None):
    # type: (Literal[None], Optional[bool], Optional[bool]) -> Callable[[FMT], FMT]
    pass


def frozen(cls=None, classes=None, instances=None):  # TODO: this_class != subclasses?
    """
    Class decorator that prevents changing the attribute values for classes and/or
    their instances after they have been initialized.

    :param cls: Class to be decorated.

    :param classes: Whether to freeze class and subclasses attributes.
    :type classes: bool or None

    :param instances: Whether to freeze instance attributes.
    :type instances: bool or None

    :return: Decorated class.
    """

    def decorator(_cls):
        # type: (FMT) -> FMT

        # Resolve parameters.
        if classes is None and instances is None:
            _classes = True
            _instances = True
        elif classes is not None and instances is None:
            _classes = bool(classes)
            _instances = getattr(_cls, _FROZEN_OBJECT_TAG, False)
        elif classes is None and instances is not None:
            _classes = getattr(_cls, _FROZEN_CLASS_TAG, False)
            _instances = bool(instances)
        else:
            _classes = bool(classes)
            _instances = bool(instances)

        # Check for metaclass.
        if not isinstance(_cls, FrozenMeta):
            error_ = "can't use 'frozen' decorator with non-{} class {}".format(
                FrozenMeta.__name__, repr(_cls.__name__)
            )
            raise TypeError(error_)

        # Decorate class.
        type.__setattr__(_cls, _FROZEN_DECORATED_TAG, True)

        # Freeze classes and future subclasses.
        if _classes:
            type.__setattr__(_cls, _FROZEN_CLASS_TAG, True)
            type.__setattr__(_cls, _FROZEN_CLASS_INSTANCE_TAG, True)
        elif getattr(_cls, _FROZEN_CLASS_TAG, False):
            error_ = "can't un-freeze class {}".format(repr(_cls.__name__))
            raise TypeError(error_)

        # Freeze future instances.
        if _instances:
            type.__setattr__(_cls, _FROZEN_OBJECT_TAG, True)
        elif getattr(_cls, _FROZEN_OBJECT_TAG, False):
            error_ = "can't un-freeze instances of {}".format(repr(_cls.__name__))
            raise TypeError(error_)

        # Dynamically replace methods.
        super_setattr = _cls.__dict__.get("__setattr__")
        super_delattr = _cls.__dict__.get("__delattr__")

        def __setattr__(self, name, value):
            if getattr(self, FROZEN_SLOT, False):
                error = "instances of {} are frozen, can't set attribute".format(
                    repr(type(self).__name__)
                )
                raise AttributeError(error)
            elif super_setattr is not None:
                super_setattr(self, name, value)
            else:
                super(_cls, self).__setattr__(name, value)

        def __delattr__(self, name):
            if getattr(self, FROZEN_SLOT, False):
                error = "instances of {} are frozen, can't delete attribute".format(
                    repr(type(self).__name__)
                )
                raise AttributeError(error)
            elif super_delattr is not None:
                super_delattr(self, name)
            else:
                super(_cls, self).__delattr__(name)

        __setattr__.__module__ = __delattr__.__module__ = _cls.__module__

        __setattr__.__name__ = "__setattr__"
        __delattr__.__name__ = "__delattr__"

        if hasattr(_cls, "__qualname__"):
            __setattr__.__qualname__ = ".".join((_cls.__qualname__, "__setattr__"))
            __delattr__.__qualname__ = ".".join((_cls.__qualname__, "__delattr__"))

        type.__setattr__(_cls, "__setattr__", __setattr__)
        type.__setattr__(_cls, "__delattr__", __delattr__)

        return _cls

    # Return decorator or decorated depending on parameters.
    if cls is None:
        return decorator
    else:
        return decorator(cls)


def freeze(obj):
    """
    Freeze an instance.

    :param obj: Instance.
    """
    cls = type(obj)

    if not isinstance(cls, FrozenMeta):
        error = "class {} does not have {} as its metaclass, can't freeze".format(
            repr(cls.__name__), repr(FrozenMeta.__name__)
        )
        raise TypeError(error)

    if hasattr(obj, "__dict__") or hasattr(cls, FROZEN_SLOT):

        # Freeze this instance.
        if not getattr(obj, FROZEN_SLOT, False):
            object.__setattr__(obj, FROZEN_SLOT, True)

    else:

        # Could not freeze slotted object, missing slot.
        error = (
            "could not freeze slotted instance of '{}.{}' since it doesn't "
            "have a slot named {} (available as a constant at {}.{})"
        ).format(
            cls.__module__,
            getattr(cls, "__qualname__", cls.__name__),
            repr(FROZEN_SLOT),
            __name__,
            "FROZEN_SLOT",
        )
        raise AttributeError(error)


class FrozenMeta(type):
    """Enables classes to be decorated with the 'frozen' decorator."""

    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):
        cls = super(FrozenMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)

        # Un-freeze this class momentarily.
        type.__setattr__(cls, _FROZEN_CLASS_INSTANCE_TAG, False)

        return cls

    def __init__(cls, name, bases, dct, **kwargs):
        super(FrozenMeta, cls).__init__(name, bases, dct, **kwargs)

        # Freeze this class.
        type.__setattr__(
            cls, _FROZEN_CLASS_INSTANCE_TAG, getattr(cls, _FROZEN_CLASS_TAG, False)
        )

    def __call__(cls, *args, **kwargs):

        # Has to be decorated.
        if not getattr(cls, _FROZEN_DECORATED_TAG, False):
            error = (
                "did not decorate class {} or any of its bases with {} decorator"
            ).format(repr(cls.__name__), repr(frozen.__name__))
            raise TypeError(error)

        # Make instance.
        self = super(FrozenMeta, cls).__call__(*args, **kwargs)

        # Freeze automatically if tagged.
        if getattr(cls, _FROZEN_OBJECT_TAG, False):
            freeze(self)

        return self

    def __setattr__(cls, name, value):
        if getattr(cls, _FROZEN_CLASS_TAG, False) and cls.__dict__.get(
            _FROZEN_CLASS_INSTANCE_TAG, False
        ):
            error = "{} is frozen, can't set class attribute".format(repr(cls.__name__))
            raise AttributeError(error)
        else:
            super(FrozenMeta, cls).__setattr__(name, value)

    def __delattr__(cls, name):
        if getattr(cls, _FROZEN_CLASS_TAG, False) and cls.__dict__.get(
            _FROZEN_CLASS_INSTANCE_TAG, False
        ):
            error = "{} is frozen, can't delete class attribute".format(
                repr(cls.__name__)
            )
            raise AttributeError(error)
        else:
            super(FrozenMeta, cls).__delattr__(name)
