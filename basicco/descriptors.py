"""Configurable descriptors."""

import collections

import six
from tippo import Any, Dict, Iterable, List, Mapping, Tuple, Type, TypeVar, Union

from .get_mro import get_mro
from .mangling import mangle
from .mapping_proxy import MappingProxyType
from .runtime_final import final
from .sentinel import SentinelType

__all__ = ["REMOVE", "Descriptor", "OwnerMeta", "Owner", "get_descriptors"]


_global_count = 0


class RemoveType(SentinelType):
    __slots__ = ()


REMOVE = RemoveType()
"""Remove sentinel value."""


class Descriptor(object):
    __slots__ = ("__owner", "__name", "__priority", "__global_count")

    def __init__(self, priority=None):
        # type: (Union[int, None]) -> None
        """
        :param priority: Priority (lower numbers mean higher priority).
        """
        global _global_count
        _global_count += 1

        self.__owner = None  # type: Union[Type[Owner], OwnerMeta, None]
        self.__name = None  # type: Union[str, None]
        self.__priority = priority  # type: Union[int, None]
        self.__global_count = _global_count  # type: int

    @final
    def __hash__(self):
        # type: () -> int
        return object.__hash__(self)

    @final
    def __eq__(self, other):
        # type: (object) -> bool
        return object.__eq__(self, other)

    @final
    def __ne__(self, other):
        # type: (object) -> bool
        return not self.__eq__(other)

    def __assign_name__(self, name):
        # type: (str) -> None
        if self.__owner is not None:
            error = "owned descriptor before naming it"
            raise AssertionError(error)
        if self.__name is not None and self.__name != name:
            error = "descriptor already named {!r}, can't name it {!r}".format(
                self.__name, name
            )
            raise TypeError(error)
        self.__name = name

    def __assign_owner__(self, owner):
        # type: (Union[Type[Owner], OwnerMeta]) -> None
        if self.__name is None:
            error = "did not assign a name to the descriptor first"
            raise AssertionError(error)
        if self.__owner is not None and self.__owner is not owner:
            error = "descriptor owned by {!r}, can't be owned by {!r}".format(
                self.__owner.__name__, owner.__name__
            )
            raise TypeError(error)
        self.__owner = owner

    def __get_required_slots__(self):  # noqa
        # type: () -> Tuple[str, ...]
        """
        Get required slot names.
        Override this method if you need slots in the owner class.

        :return: Required slot names.
        """
        return ()

    def __get_replacement__(self):
        # type: () -> Any
        """
        Get replacement.
        Override this method if you need to replace this descriptor with another object
        in the owner class.

        :return: Replacement object (or sentinel value REMOVE for removing it).
        """
        return self

    def __on_override__(self, overriden):
        # type: (Descriptor) -> None
        """
        This method gets called when this descriptor overrides a previous one.
        Override this method if you want custom behavior.

        :param overriden: The previous descriptor.
        """

    def __on_overridden__(self, override):
        # type: (Descriptor) -> None
        """
        This method gets called when this descriptor gets overridden by a new one.
        Override this method if you want custom behavior.

        :param override: The new descriptor.
        """

    @property
    @final
    def name(self):
        # type: () -> str
        """Descriptor name."""
        if self.__name is None:
            error = "descriptor not yet owned/named"
            raise TypeError(error)
        return self.__name

    @property
    @final
    def owner(self):
        # type: () -> Union[Type[Owner], OwnerMeta]
        """Owner class."""
        if self.__owner is None:
            error = "descriptor not yet owned/named"
            raise TypeError(error)
        return self.__owner

    @property
    @final
    def priority(self):
        # type: () -> Union[int, None]
        """Priority."""
        return self.__priority

    @property
    @final
    def global_count(self):
        # type: () -> int
        """Global count."""
        return self.__global_count


_D = TypeVar("_D", bound=Descriptor)


class OwnerMeta(type):
    __this_descriptors = (
        collections.OrderedDict()
    )  # type: collections.OrderedDict[str, Descriptor]
    __all_descriptors = (
        collections.OrderedDict()
    )  # type: collections.OrderedDict[str, Descriptor]

    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):
        # type: (Type[_OM], str, Tuple[Type[Any], ...], Mapping[str, Any], **Any) -> _OM
        dct = dict(dct)

        # Collect descriptors for this class.
        this_descriptors = {}  # type: Dict[str, Descriptor]
        required_slots = []  # type: List[str]
        for member_name, member in list(dct.items()):
            if isinstance(member, Descriptor):
                member.__assign_name__(member_name)
                required_slots.extend(member.__get_required_slots__())
                this_descriptors[member_name] = dct.pop(member_name)
                replacement = member.__get_replacement__()
                if replacement is not REMOVE:
                    dct[member_name] = replacement

        # Add required slots.
        slots = list(dct.get("__slots__", ()))
        for required_slot in required_slots:
            if required_slot in dct:
                error = (
                    "error building {!r}, possible conflict between required slot {!r} "
                    "and descriptor of the same name, consider also implementing "
                    "'__get_replacement__' method to avoid naming conflicts"
                ).format(name, required_slot)
                raise TypeError(error)
            if required_slot not in slots:
                slots.append(required_slot)
        dct["__slots__"] = tuple(slots)

        # Build class and assign owner to descriptors.
        cls = super(OwnerMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
        for descriptor in this_descriptors.values():
            descriptor.__assign_owner__(cls)

        # Order this class' descriptors and store them in the class.
        cls.__this_descriptors = collections.OrderedDict()
        for descriptor_name, descriptor in sorted(
            this_descriptors.items(), key=lambda i: i[1].global_count
        ):
            cls.__this_descriptors[descriptor_name] = descriptor

        # Scrape bases for descriptors.
        all_descriptors = {}  # type: Dict[str, Descriptor]
        all_descriptors_count = {}  # type: Dict[str, int]
        for base in reversed(get_mro(cls)):
            if base is object:
                continue
            if not isinstance(base, OwnerMeta):
                for member_name, member in base.__dict__.items():
                    if member_name in all_descriptors:
                        error = "non-owner base {!r} overrides descriptor {!r}".format(
                            base.__name__, member_name
                        )
                        raise TypeError(error)
                    elif isinstance(member, Descriptor):
                        error = "non-owner base {!r} defines descriptor {!r}".format(
                            base.__name__, member_name
                        )
                        raise TypeError(error)
            else:
                for descriptor_name, descriptor in base.__this_descriptors.items():
                    if descriptor_name in all_descriptors:
                        all_descriptors[descriptor_name].__on_overridden__(descriptor)
                        descriptor.__on_override__(all_descriptors[descriptor_name])
                    all_descriptors[descriptor_name] = descriptor
                    if descriptor_name not in all_descriptors_count:
                        all_descriptors_count[descriptor_name] = descriptor.global_count

        # Order descriptors by priority, global count.
        cls.__all_descriptors = collections.OrderedDict()
        sorting_key = lambda i: (
            i[1].priority
            if i[1].priority is not None
            else len(all_descriptors),  # priority
            all_descriptors_count[i[0]],  # global count
        )
        descriptor_items = sorted(all_descriptors.items(), key=sorting_key)
        for descriptor_name, descriptor in descriptor_items:
            cls.__all_descriptors[descriptor_name] = descriptor

        return cls


_OM = TypeVar("_OM", bound=OwnerMeta)


class Owner(six.with_metaclass(OwnerMeta, object)):
    """Descriptor owner."""

    __slots__ = ()


def get_descriptors(
    cls,  # type: Union[Type[Owner], OwnerMeta]
    base_cls=None,  # type: Union[Type[_D], Iterable[Type[_D]], None]
    inherited=True,  # type: bool
):
    # type: (...) -> MappingProxyType[str, _D]
    """
    Get descriptors in owner class.

    :param cls: Descriptor owner class.
    :param base_cls: Base descriptor class(es).
    :param inherited: Whether to include parent classes' descriptors.
    :return: Ordered descriptors mapped by name.
    """
    if isinstance(base_cls, Iterable):
        bases = tuple(base_cls)  # type: Tuple[Type[_D], ...]
    elif base_cls is None:
        bases = (Descriptor,)  # type: ignore
    else:
        assert base_cls is not None
        bases = (base_cls,)
    bases = bases or (Descriptor,)  # type: ignore
    for base in bases:
        if not isinstance(base, type) or not issubclass(base, Descriptor):
            error = "{!r} is not a subclass of {!r}".format(
                base.__name__, Descriptor.__name__
            )
            raise TypeError(error)

    attribute = mangle(
        "__all_descriptors" if inherited else "__this_descriptors", OwnerMeta.__name__
    )

    if bases != (Descriptor,):
        descriptors = collections.OrderedDict()
        for descriptor_name, descriptor in getattr(cls, attribute).items():
            if isinstance(descriptor, bases):  # noqa
                descriptors[descriptor_name] = descriptor
    else:
        descriptors = getattr(cls, attribute)

    return MappingProxyType(descriptors)
