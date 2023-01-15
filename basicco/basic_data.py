from enum import Enum

from tippo import Any, Iterable, SupportsKeysAndGetItem, TypeVar, cast, overload

from ._bases import SlottedBase
from .abstract_class import abstract
from .custom_repr import mapping_repr
from .explicit_hash import set_to_none
from .hash_cache_wrapper import HashCacheWrapper
from .mangling import mangle
from .recursive_repr import recursive_repr
from .safe_repr import safe_repr

__all__ = ["ItemUsecase", "BasicData", "ImmutableBasicData"]


class ItemUsecase(Enum):
    EQ = "EQ"
    HASH = "HASH"
    REPR = "REPR"
    INIT = "INIT"


class BasicData(SlottedBase):
    __slots__ = ("__hash_cache__",)

    @safe_repr
    @recursive_repr
    def __repr__(self):
        repr_items = self.__items__(ItemUsecase.REPR)
        init_keys = frozenset(dict(self.__items__(ItemUsecase.INIT)))
        template = lambda i, key, value, _init_keys=init_keys: (
            "{}={}".format(key, value) if key in _init_keys else "<{}={}>".format(key, value)
        )
        return mapping_repr(
            mapping=repr_items,
            prefix="{}(".format(type(self).__qualname__),
            template=template,
            suffix=")",
            key_repr=str,
        )

    def __getitem__(self, key):
        # type: (str) -> Any
        return self.to_dict()[key]

    @set_to_none
    def __hash__(self):
        error = "{!r} object is not hashable".format(type(self).__qualname__)
        raise TypeError(error)

    def __eq__(self, other):
        return type(other) is type(self) and self.__items__(ItemUsecase.EQ) == other.__items__(ItemUsecase.EQ)

    @abstract
    def __items__(self, usecase=None):
        # type: (ItemUsecase | None) -> list[tuple[str, Any]]
        raise NotImplementedError()


class ImmutableBasicData(BasicData):
    __slots__ = ()

    def __copy__(self):
        new_self = super(ImmutableBasicData, self).__copy__()
        if hasattr(new_self, "__hash_cache__"):
            del new_self.__hash_cache__
        return new_self

    def __hash__(self):
        # type: () -> int
        try:
            cached_hash = self.__hash_cache__  # type: ignore
            if cached_hash is None:
                raise AttributeError()
        except AttributeError:
            hash_items = tuple(self.__items__(ItemUsecase.HASH))
            unsafe_attributes = set(hash_items).difference(self.__items__(ItemUsecase.EQ))
            if unsafe_attributes:
                error = "unsafe hash, attributes {} contribute to the hash but don't contribute to the eq".format(
                    ", ".join(repr(a) for a in sorted(unsafe_attributes))
                )
                raise RuntimeError(error)
            self.__hash_cache__ = HashCacheWrapper(hash(hash_items))  # type: HashCacheWrapper | None
            cached_hash = self.__hash_cache__  # type: ignore
        return cast(int, cached_hash)

    def __setattr__(self, name, value):
        # type: (str, Any) -> None
        if not name.startswith("_") and (hasattr(self, name) and not hasattr(type(self), name)):
            error = "{!r} object is immutable".format(type(self).__name__)
            raise AttributeError(error)
        if name != mangle("__hash_cache__", ImmutableBasicData.__name__):
            self.__hash_cache__ = None
        super(ImmutableBasicData, self).__setattr__(name, value)

    def __delattr__(self, name):
        # type: (str) -> None
        if not name.startswith("_"):
            error = "{!r} object is immutable".format(type(self).__name__)
            raise AttributeError(error)
        if name != mangle("__hash_cache__", ImmutableBasicData.__name__):
            self.__hash_cache__ = None
        super(ImmutableBasicData, self).__delattr__(name)


IBD = TypeVar("IBD", bound=ImmutableBasicData)


def to_dict(self, usecase=None):
    # type: (ItemUsecase | None) -> dict[str, Any]
    return dict(self.__items__(usecase=usecase))


def keys(self, usecase=None):
    #  type: (ItemUsecase | None) -> tuple[str, ...]
    return tuple(k for k, _ in self.__items__(usecase=usecase))
