"""Mapping Proxy type (read-only) for older Python versions."""

__all__ = ["MappingProxyType"]


try:
    from types import MappingProxyType

except ImportError:
    from tippo import Iterator, Mapping, TypeVar

    _KT = TypeVar("_KT")
    _VT = TypeVar("_VT")

    class _MappingProxyType(Mapping[_KT, _VT]):
        __slots__ = ("__mapping",)

        def __init__(self, mapping):
            # type: (Mapping[_KT, _VT]) -> None
            self.__mapping = mapping

        def __getitem__(self, item):
            # type: (_KT) -> _VT
            return self.__mapping[item]

        def __len__(self):
            # type: () -> int
            return len(self.__mapping)

        def __iter__(self):
            # type: () -> Iterator[_KT]
            for key in self.__mapping:
                yield key

    type.__setattr__(_MappingProxyType, "__name__", "MappingProxyType")
    type.__setattr__(_MappingProxyType, "__qualname__", "MappingProxyType")
    globals()["MappingProxyType"] = _MappingProxyType
