"""Mapping Proxy type (read-only) for older Python versions."""

__all__ = ["MappingProxyType"]


try:
    from types import MappingProxyType

except ImportError:
    from tippo import Mapping, Iterator, TypeVar  # type: ignore

    KT = TypeVar("KT")
    VT = TypeVar("VT")

    class MappingProxyType(Mapping[KT, VT]):  # type: ignore
        __slots__ = ("__mapping",)

        def __init__(self, mapping):
            # type: (Mapping[KT, VT]) -> None
            self.__mapping = mapping

        def __getitem__(self, item):
            # type: (KT) -> VT
            return self.__mapping[item]

        def __len__(self):
            # type: () -> int
            return len(self.__mapping)

        def __iter__(self):
            # type: () -> Iterator[KT]
            for key in self.__mapping:
                yield key
