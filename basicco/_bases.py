import six

from .dirable import Dirable, DirableMeta
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

__all__ = ["BaseMeta", "Base", "BetterBaseMeta", "BetterBase", "final", "unlocked_context", "set_locked", "is_locked"]


class BaseMeta(
    InitSubclassMeta, DirableMeta, ImplicitHashMeta, ReducibleMeta, QualnamedMeta, SafeNotEqualsMeta, SetNameMeta
):
    """Metaclass for better compatibility amongst different Python versions."""


class Base(
    six.with_metaclass(BaseMeta, InitSubclass, Dirable, ImplicitHash, Reducible, Qualnamed, SafeNotEquals, SetName)
):
    """Class for better compatibility amongst different Python versions."""

    __slots__ = ()


class BetterBaseMeta(LockedClassMeta, ExplicitHashMeta, NamespacedMeta, RuntimeFinalMeta, BaseMeta):
    """Metaclass that adds features to the basic `type`."""


class BetterBase(six.with_metaclass(BetterBaseMeta, LockedClass, ExplicitHash, Namespaced, RuntimeFinal, Base)):
    """Class that adds features to the basic `object`."""

    __slots__ = ()
