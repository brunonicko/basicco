from sys import version_info

from .utils.reducer import reducer

__all__ = [
    "ReducibleMeta",
]


class ReducibleMeta(type):
    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):
        cls = super(ReducibleMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
        if version_info[0:2] < (3, 4):
            if getattr(cls, "__reduce__", None) is object.__reduce__:
                type.__setattr__(cls, "__reduce__", reducer)
        return cls
