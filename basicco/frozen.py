"""Prevents modifying class and/or instance attributes."""

from functools import wraps
from inspect import isclass
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import Any, Callable, TypeVar, Optional, Literal

    FMT = TypeVar("FMT", bound="FrozenMeta")

__all__ = [
    "FROZEN_SLOT",
    "frozen",
    "freeze",
    "is_frozen",
    "will_class_be_frozen",
    "will_subclasses_be_frozen",
    "will_instance_be_frozen",
    "FrozenMeta",
]

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


def frozen(cls=None, classes=None, instances=None):
    """
    Class decorator that permanently prevents changing the attribute values for classes
    & subclases, and/or their instances after they have been initialized.

    :param cls: Class to be decorated.

    :param classes: Whether to permanently freeze class and subclasses attributes.
    :type classes: bool or None

    :param instances: Whether to permanently freeze instance attributes.
    :type instances: bool or None

    :return: Decorated class.

    :raises TypeError: Provided invalid class.
    :raises TypeError: Can't unfreeze already frozen class.
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
            if not isclass(_cls):
                error_ = "{} object is not a class".format(repr(type(cls).__name__))
            else:
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
            error_ = "can't un-freeze permanently frozen class {}".format(
                repr(_cls.__name__)
            )
            raise TypeError(error_)

        # Freeze future instances.
        if _instances:
            type.__setattr__(_cls, _FROZEN_OBJECT_TAG, True)
        elif getattr(_cls, _FROZEN_OBJECT_TAG, False):
            error_ = "can't un-freeze permanently frozen instances of {}".format(
                repr(_cls.__name__)
            )
            raise TypeError(error_)

        # Dynamically replace methods.
        super_setattr = _cls.__dict__.get("__setattr__")
        super_delattr = _cls.__dict__.get("__delattr__")

        def __setattr__(self, name, value):
            if getattr(self, FROZEN_SLOT, False):
                error = "{} instance is frozen, can't set attribute".format(
                    repr(type(self).__name__)
                )
                raise AttributeError(error)
            elif super_setattr is not None:
                super_setattr(self, name, value)
            else:
                super(_cls, self).__setattr__(name, value)

        def __delattr__(self, name):
            if getattr(self, FROZEN_SLOT, False):
                error = "{} instance is frozen, can't delete attribute".format(
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

        if super_setattr is not None:
            __setattr__ = wraps(super_setattr)(__setattr__)
        if super_delattr is not None:
            __delattr__ = wraps(super_delattr)(__delattr__)

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
    Freeze an instance or class.

    :param obj: Instance or Class.

    :return: Instance of Class.
    """
    is_class = isinstance(obj, type)
    if is_class:
        cls = obj
    else:
        cls = type(obj)

    # Check metaclass.
    if not isinstance(cls, FrozenMeta):
        error = "class {} does not have {} as its metaclass, can't freeze".format(
            repr(cls.__name__), repr(FrozenMeta.__name__)
        )
        raise TypeError(error)

    # Decorate if necessary.
    if not getattr(cls, _FROZEN_DECORATED_TAG, False):
        cls = frozen(cls, classes=False, instances=False)

    if is_class:

        # Freeze this class.
        type.__setattr__(cls, _FROZEN_CLASS_INSTANCE_TAG, True)

    else:

        # Freeze instance.
        if hasattr(obj, "__dict__") or hasattr(cls, FROZEN_SLOT):
            if not getattr(obj, FROZEN_SLOT, False):
                object.__setattr__(obj, FROZEN_SLOT, True)
        else:
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

    return obj


def is_frozen(obj):
    # type: (Any) -> bool
    """
    Tells whether a class or instance is frozen.

    :param obj: Class or instance.

    :return: True if it is frozen.
    :rtype: bool
    """
    if isclass(obj):
        return obj.__dict__.get(_FROZEN_CLASS_INSTANCE_TAG, False) is True
    else:
        return getattr(obj, FROZEN_SLOT, False) is True


def will_class_be_frozen(cls):
    # type: (FrozenMeta) -> bool
    """
    Tells whether a class will be frozen after initialization.
    If already initialized, tells whether it is frozen.

    :param cls: Class.

    :return: True if it will be/is frozen.
    :rtype: bool

    :raises TypeError: Did not provide a class.
    """
    if not isclass(cls):
        error = "{} object is not a class".format(repr(type(cls).__name__))
        raise TypeError(error)
    return (
        getattr(cls, _FROZEN_CLASS_TAG, False) is True
        or cls.__dict__.get(_FROZEN_CLASS_INSTANCE_TAG, False) is True
    )


def will_subclasses_be_frozen(cls):
    # type: (FrozenMeta) -> bool
    """
    Tells whether class and its subclasses will be frozen after initialization.

    :param cls: Class.

    :return: True if will be frozen.
    :rtype: bool

    :raises TypeError: Did not provide a class.
    """
    if not isclass(cls):
        error = "{} object is not a class".format(repr(type(cls).__name__))
        raise TypeError(error)
    return getattr(cls, _FROZEN_CLASS_TAG, False) is True


def will_instance_be_frozen(instance):
    """
    Tells whether an instance will be frozen after initialization.
    If already initialized, tells whether it is frozen.

    :param instance: Instance.

    :return: True if it will be/is frozen.
    :rtype: bool

    :raises TypeError: Did not provide an instance.
    """
    if isclass(instance):
        error = "{} is a class, not an instance".format(repr(instance.__name__))
        raise TypeError(error)
    return (
        getattr(type(instance), _FROZEN_OBJECT_TAG, False) is True
        or getattr(instance, FROZEN_SLOT, False) is True
    )


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
        self = super(FrozenMeta, cls).__call__(*args, **kwargs)

        # Freeze this instance.
        if getattr(cls, _FROZEN_OBJECT_TAG, False):
            freeze(self)

        return self

    def __setattr__(cls, name, value):
        if cls.__dict__.get(_FROZEN_CLASS_INSTANCE_TAG, False):
            error = "class {} is frozen, can't set class attribute".format(
                repr(cls.__name__)
            )
            raise AttributeError(error)
        else:
            super(FrozenMeta, cls).__setattr__(name, value)

    def __delattr__(cls, name):
        if cls.__dict__.get(_FROZEN_CLASS_INSTANCE_TAG, False):
            error = "class {} is frozen, can't delete class attribute".format(
                repr(cls.__name__)
            )
            raise AttributeError(error)
        else:
            super(FrozenMeta, cls).__delattr__(name)
