from ._bases import (
    Base,
    BaseMeta,
    CompatBase,
    CompatBaseMeta,
    final,
    is_locked,
    set_locked,
    unlocked_context,
)

__all__ = ["CompatBaseMeta", "CompatBase", "BaseMeta", "Base", "final", "unlocked_context", "set_locked", "is_locked"]


# Set module to this one.
for cls in (CompatBaseMeta, CompatBase, BaseMeta, Base):
    type.__setattr__(cls, "__module__", __name__)


# TODO: metaclass that auto-decorates reprs?
# TODO: metaclass for better abstraction support (including abstract() descriptor)
# TODO: rename qualname to qualified_name?
# TODO: rename default_dir to something better?
# TODO: find corresponding peps and add to readme/docs
