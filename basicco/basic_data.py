from enum import Enum

from tippo import Any, Iterable, SupportsKeysAndGetItem, TypeVar, cast, overload

from ._bases import Base
from .abstract_class import abstract
from .custom_repr import mapping_repr
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


class BasicData(Base):
    __slots__ = ()

    @safe_repr
    @recursive_repr
    def __repr__(self):
        repr_items = self.to_items(ItemUsecase.REPR)
        init_keys = frozenset(dict(self.to_items(ItemUsecase.INIT)))
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

    def __hash__(self):
        error = "{!r} object is not hashable".format(type(self).__qualname__)
        raise TypeError(error)

    def __eq__(self, other):
        return type(other) is type(self) and self.to_items(ItemUsecase.EQ) == other.to_items(ItemUsecase.EQ)

    def to_dict(self, usecase=None):
        # type: (ItemUsecase) -> dict[str, Any]
        return dict(self.to_items(usecase=usecase))

    @abstract
    def to_items(self, usecase=None):
        # type: (ItemUsecase | None) -> list[tuple[str, Any]]
        raise NotImplementedError()

    def keys(self, usecase=None):
        #  type: (ItemUsecase) -> tuple[str, ...]
        return tuple(k for k, _ in self.to_items(usecase=usecase))


type.__setattr__(BasicData, "__hash__", None)


class ImmutableBasicData(BasicData):
    __slots__ = ("__cached_hash",)

    def __hash__(self):
        # type: () -> int
        try:
            cached_hash = self.__cached_hash  # type: ignore
            if cached_hash is None:
                raise AttributeError()
        except AttributeError:
            hash_items = tuple(self.to_items(ItemUsecase.HASH))
            unsafe_attributes = set(hash_items).difference(self.to_items(ItemUsecase.EQ))
            if unsafe_attributes:
                error = "unsafe hash, attributes {} contribute to the hash but don't contribute to the eq".format(
                    ", ".join(repr(a) for a in sorted(unsafe_attributes))
                )
                raise RuntimeError(error)
            self.__cached_hash = HashCacheWrapper(hash(hash_items))  # type: HashCacheWrapper | None
            cached_hash = self.__cached_hash  # type: ignore
        return cast(int, cached_hash)

    def __setattr__(self, name, value):
        # type: (str, Any) -> None
        if not name.startswith("_") and (hasattr(self, name) and not hasattr(type(self), name)):
            error = "{!r} object is immutable".format(type(self).__name__)
            raise AttributeError(error)
        if name != mangle("__cached_hash", ImmutableBasicData.__name__):
            self.__cached_hash = None
        super(ImmutableBasicData, self).__setattr__(name, value)

    def __delattr__(self, name):
        # type: (str) -> None
        if not name.startswith("_"):
            error = "{!r} object is immutable".format(type(self).__name__)
            raise AttributeError(error)
        if name != mangle("__cached_hash", ImmutableBasicData.__name__):
            self.__cached_hash = None
        super(ImmutableBasicData, self).__delattr__(name)

    def _set_attr(self, name, value):
        # type: (str, Any) -> None
        """
        Internally set attribute.
        Can be useful for setting lazily calculated values.
        Use with caution.

        :param name: Attribute name.
        :param value: Value.
        """
        self.__cached_hash = None
        super(ImmutableBasicData, self).__setattr__(name, value)

    def _del_attr(self, name):
        # type: (str) -> None
        """
        Internally delete attribute.
        Can be useful for resetting lazily calculated values.
        Use with caution.

        :param name: Attribute name.
        """
        self.__cached_hash = None
        super(ImmutableBasicData, self).__delattr__(name)

    @overload
    def update(self, __m, **kwargs):
        # type: (IBD, SupportsKeysAndGetItem[str, Any], **Any) -> IBD
        pass

    @overload
    def update(self, __m, **kwargs):
        # type: (IBD, Iterable[tuple[str, Any]], **Any) -> IBD
        pass

    @overload
    def update(self, **kwargs):
        # type: (IBD, **Any) -> IBD
        pass

    @abstract
    def update(self, *args, **kwargs):
        """
        Make a new version with updates.

        :params: Same parameters as `dict`.
        :return: Updated version.
        """
        raise NotImplementedError()


IBD = TypeVar("IBD", bound=ImmutableBasicData)
