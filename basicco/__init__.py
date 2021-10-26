from sys import version_info

from six import with_metaclass

from .generic import GenericMeta
from .abstract import abstract, is_abstract, is_abstract_member, AbstractMeta
from .final import final, is_final, is_final_member, FinalMeta
from .qualname import qualname, QualnameMeta
from .frozen import frozen, FrozenMeta, FROZEN_SLOT
from .utils.reducer import reducer

__all__ = [
    "Base",
    "BaseMeta",
    "abstract",
    "is_abstract",
    "is_abstract_member",
    "final",
    "is_final",
    "is_final_member",
    "qualname",
    "frozen",
]


class BaseMeta(FrozenMeta, FinalMeta, AbstractMeta, QualnameMeta, GenericMeta):
    """Metaclass for :class:`Base`."""


class Base(with_metaclass(BaseMeta, object)):
    """Base class."""

    __slots__ = (FROZEN_SLOT,)

    if version_info[0:2] < (3, 4):
        __reduce__ = reducer


def _lock(mcs):  # TODO: replace with possible `frozen` functionality?
    def __setattr__(cls, name, value):
        if cls is Base:
            error = "can't set attributes of {} class".format(repr(Base.__name__))
            raise AttributeError(error)
        else:
            super(mcs, cls).__setattr__(name, value)

    def __delattr__(cls, name):
        if cls is Base:
            error = "can't delete attributes of {} class".format(repr(Base.__name__))
            raise AttributeError(error)
        else:
            super(mcs, cls).__delattr__(name)

    type.__setattr__(mcs, "__setattr__", __setattr__)
    type.__setattr__(mcs, "__delattr__", __delattr__)


_lock(BaseMeta)
