import sys

from .get_mro import get_mro

__all__ = ["InitSubclassMeta"]


class InitSubclassMeta(type):
    def __init__(cls, name, bases, dct, **kwargs):
        body_kwargs = {}

        conflicting_kwargs = set(body_kwargs).intersection(kwargs)
        if conflicting_kwargs:
            error = "conflicting class arguments {}".format(", ".join(sorted(repr(k) for k in conflicting_kwargs)))
            raise TypeError(error)
        kwargs.update(body_kwargs)

        if sys.version_info[:3] < (3, 6):
            assert not kwargs
            super(InitSubclassMeta, cls).__init__(name, bases, dct)
            method = None
            for base in reversed(get_mro(cls)):
                if base is object:
                    continue
                if base is cls:
                    break
                method = base.__dict__.get("__init_subclass__")

            if method is not None:
                method(cls, **body_kwargs)
        else:
            super(InitSubclassMeta, cls).__init__(name, bases, dct, **kwargs)
