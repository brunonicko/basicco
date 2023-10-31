import six
import slotted
from tippo import GenericMeta, TypeVar

from basicco.abstract_class import Abstract, AbstractMeta, abstract, is_abstract
from basicco.default_dir import DefaultDir, DefaultDirMeta
from basicco.explicit_hash import ExplicitHash, ExplicitHashMeta
from basicco.implicit_hash import ImplicitHash, ImplicitHashMeta
from basicco.init_subclass import InitSubclass, InitSubclassMeta
from basicco.locked_class import (
    LockedClass,
    LockedClassMeta,
    is_locked,
    set_locked,
    unlocked_context,
)
from basicco.namespace import Namespaced, NamespacedMeta
from basicco.obj_state import Reducible, ReducibleMeta, get_state, update_state
from basicco.qualname import Qualnamed, QualnamedMeta
from basicco.runtime_final import RuntimeFinal, RuntimeFinalMeta, final
from basicco.safe_not_equals import SafeNotEquals, SafeNotEqualsMeta
from basicco.set_name import SetName, SetNameMeta

__all__ = [
    "CompatBaseMeta",
    "CompatBase",
    "BaseMeta",
    "Base",
    "SlottedBaseMeta",
    "SlottedBase",
    "abstract",
    "is_abstract",
    "final",
    "unlocked_context",
    "set_locked",
    "is_locked",
]


class CompatBaseMeta(
    InitSubclassMeta,
    DefaultDirMeta,
    ImplicitHashMeta,
    ReducibleMeta,
    QualnamedMeta,
    SafeNotEqualsMeta,
    SetNameMeta,
    AbstractMeta,
    GenericMeta,
):
    """Base metaclass for better compatibility amongst different Python versions."""


class CompatBase(
    six.with_metaclass(
        CompatBaseMeta,
        InitSubclass,
        DefaultDir,
        ImplicitHash,
        Reducible,
        Qualnamed,
        SafeNotEquals,
        SetName,
        Abstract,
    )
):
    """Base class for better compatibility amongst different Python versions."""

    __slots__ = ()


class BaseMeta(
    LockedClassMeta,
    ExplicitHashMeta,
    NamespacedMeta,
    RuntimeFinalMeta,
    CompatBaseMeta,
    GenericMeta,
):
    """Base metaclass that adds extra features to the basic `type`."""


class Base(
    six.with_metaclass(
        BaseMeta,
        LockedClass,
        ExplicitHash,
        Namespaced,
        RuntimeFinal,
        CompatBase,
    )
):
    """Base class that adds extra features to the basic `object`."""

    __slots__ = ("__weakref__",)

    def __copy__(self):
        # type: (_B) -> _B
        cls = type(self)
        new_self = cls.__new__(cls)
        update_state(new_self, get_state(self))
        return new_self


_B = TypeVar("_B", bound=Base)


class SlottedBaseMeta(BaseMeta, slotted.SlottedABCGenericMeta):
    """Slotted base metaclass."""


class SlottedBase(six.with_metaclass(SlottedBaseMeta, Base, slotted.SlottedABC)):
    """Slotted base class."""

    __slots__ = ()
