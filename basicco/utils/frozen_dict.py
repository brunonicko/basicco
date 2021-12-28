"""Frozen dictionary implementation."""

from typing import TYPE_CHECKING, TypeVar

from .wrapped_dict import WrappedDict

if TYPE_CHECKING:
    from typing import Optional, Mapping

__all__ = ["FrozenDict"]


KT = TypeVar("KT")
VT = TypeVar("VT")


class FrozenDict(WrappedDict[KT, VT]):
    """Frozen dictionary."""

    __slots__ = ()

    def __init__(self, mapping=None):
        # type: (Optional[Mapping[KT, VT]]) -> None
        if mapping is not None:
            mapping = dict(mapping)
        super(FrozenDict, self).__init__(mapping)
