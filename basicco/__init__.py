from ._bases import (
    Base,
    BaseMeta,
    CompatBase,
    CompatBaseMeta,
    SlottedBase,
    SlottedBaseMeta,
    abstract,
    final,
    is_abstract,
    is_locked,
    set_locked,
    unlocked_context,
)

__all__ = [
    "CompatBaseMeta",
    "CompatBase",
    "BaseMeta",
    "Base",
    "SlottedBase",
    "SlottedBaseMeta",
    "abstract",
    "is_abstract",
    "final",
    "unlocked_context",
    "set_locked",
    "is_locked",
]


# Set module to this one.
for cls in (CompatBaseMeta, CompatBase, BaseMeta, Base, SlottedBaseMeta, SlottedBase):
    type.__setattr__(cls, "__module__", __name__)
