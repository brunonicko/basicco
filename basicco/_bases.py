import six
import slotted
from tippo import GenericMeta

from .abstract_class import Abstract, AbstractMeta, abstract, is_abstract
from .default_dir import DefaultDir, DefaultDirMeta
from .explicit_hash import ExplicitHash, ExplicitHashMeta
from .implicit_hash import ImplicitHash, ImplicitHashMeta
from .init_subclass import InitSubclass, InitSubclassMeta
from .locked_class import (
    LockedClass,
    LockedClassMeta,
    is_locked,
    set_locked,
    unlocked_context,
)
from .namespace import Namespaced, NamespacedMeta
from .obj_state import Reducible, ReducibleMeta
from .qualname import Qualnamed, QualnamedMeta
from .runtime_final import RuntimeFinal, RuntimeFinalMeta, final
from .safe_not_equals import SafeNotEquals, SafeNotEqualsMeta
from .set_name import SetName, SetNameMeta

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


class SlottedBaseMeta(BaseMeta, slotted.SlottedABCGenericMeta):
    """Slotted base metaclass."""


class SlottedBase(six.with_metaclass(SlottedBaseMeta, Base, slotted.SlottedABC)):
    """Slotted base class."""

    __slots__ = ()
