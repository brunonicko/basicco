from ._bases import Base, BaseMeta, BetterBase, BetterBaseMeta

__all__ = ["BaseMeta", "Base", "BetterBaseMeta", "BetterBase"]


for cls in (BaseMeta, Base, BetterBaseMeta, BetterBase):
    type.__setattr__(cls, "__module__", __name__)


# TODO: integration tests for bases
# TODO: metaclass that auto-decorates reprs?
# TODO: metaclass for better abstraction support (including abstract() descriptor)
# TODO: rename qualname to qualified_name?
# TODO: rename dirable to something better?
# TODO: find corresponding peps and add to readme/docs
# TODO: base classes should be the main attraction
# TODO: motivation, python 2 compatibility for vfx
# TODO: separate docs by compat/features
