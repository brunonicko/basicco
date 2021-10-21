from sys import version_info

from slotted import SlottedABC, SlottedABCMeta
from six import with_metaclass

from .generic import GenericMeta
from .abstract import AbstractMeta
from .final import FinalMeta
from .qualname import QualnameMeta
from .frozen import FrozenMeta, FROZEN_SLOT
from .final import final
from .qualname import qualname
from .frozen import frozen
from .utils.reducer import reducer

__all__ = ["Base", "BaseMeta", "final", "qualname", "frozen"]


class BaseMeta(
    FrozenMeta, QualnameMeta, FinalMeta, AbstractMeta, SlottedABCMeta, GenericMeta
):
    pass


class Base(with_metaclass(BaseMeta, object)):
    __slots__ = (FROZEN_SLOT,)

    if version_info[0:2] < (3, 4):
        __reduce__ = reducer


SlottedABC.register(Base)
