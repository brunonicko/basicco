from six import with_metaclass

from .generic import GenericMeta
from .reducible import ReducibleMeta
from .explicit_hash import ExplicitHashMeta
from .namespaced import NamespacedMeta
from .abstract import abstract, is_abstract, is_abstract_member, AbstractMeta
from .final import final, is_final, is_final_member, FinalMeta
from .qualified import get_qualified_name, QualifiedMeta
from .frozen import (
    FROZEN_SLOT,
    frozen,
    freeze,
    is_frozen,
    will_class_be_frozen,
    will_subclasses_be_frozen,
    will_instance_be_frozen,
    FrozenMeta,
)
from .utils.reducer import reducer
from .utils.namespace import Namespace

__all__ = [
    "Base",
    "BaseMeta",
    "abstract",
    "is_abstract",
    "is_abstract_member",
    "final",
    "is_final",
    "is_final_member",
    "get_qualified_name",
    "frozen",
    "freeze",
    "is_frozen",
    "will_class_be_frozen",
    "will_subclasses_be_frozen",
    "will_instance_be_frozen",
]


class BaseMeta(
    FrozenMeta,
    FinalMeta,
    AbstractMeta,
    QualifiedMeta,
    NamespacedMeta,
    ExplicitHashMeta,
    ReducibleMeta,
    GenericMeta,
):
    """Metaclass for :class:`Base`."""


class Base(with_metaclass(BaseMeta, object)):
    """Base class."""

    __slots__ = (FROZEN_SLOT,)
