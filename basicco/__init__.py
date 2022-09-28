from ._bases import CompatBase, CompatBaseMeta, Base, BaseMeta, final, unlocked_context, set_locked, is_locked

__all__ = ["CompatBaseMeta", "CompatBase", "BaseMeta", "Base", "final", "unlocked_context", "set_locked", "is_locked"]


# Set module to this one.
for cls in (CompatBaseMeta, CompatBase, BaseMeta, Base):
    type.__setattr__(cls, "__module__", __name__)


# TODO: integration tests for bases
# TODO: metaclass that auto-decorates reprs?
# TODO: metaclass for better abstraction support (including abstract() descriptor)
# TODO: rename qualname to qualified_name?
# TODO: rename default_dir to something better?
# TODO: find corresponding peps and add to readme/docs
# TODO: base classes should be the main attraction
# TODO: motivation, python 2 compatibility for vfx
# TODO: separate docs by compat/features
