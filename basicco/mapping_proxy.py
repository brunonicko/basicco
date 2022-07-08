"""Mapping Proxy type (read-only) for older Python versions."""

from __future__ import absolute_import, division, print_function

__all__ = ["MappingProxyType"]


try:
    from types import MappingProxyType

except ImportError:
    from collections import Mapping  # type: ignore

    class MappingProxyType(Mapping):  # type: ignore
        __slots__ = ("__mapping",)

        def __init__(self, mapping):
            self.__mapping = mapping

        def __getitem__(self, item):
            return self.__mapping[item]

        def __len__(self):
            return len(self.__mapping)

        def __iter__(self):
            for key in self.__mapping:
                yield key
