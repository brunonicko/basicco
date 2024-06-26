# type: ignore

import collections

import pytest
from six import with_metaclass
from tippo import Any, Dict, Generic, GenericMeta, TypeVar

from basicco import CompatBase, CompatBaseMeta
from basicco.descriptors import REMOVE, Descriptor, Owner, OwnerMeta, get_descriptors
from basicco.mapping_proxy import MappingProxyType

T = TypeVar("T")


class SlotDescriptor(Descriptor):
    __slots__ = ("shared",)

    def __init__(self, shared, priority=None):
        super(SlotDescriptor, self).__init__(priority)
        self.shared = shared  # type: Dict[str, Any]

    def __get_required_slots__(self):
        return (self.name,)

    def __get_replacement__(self):
        return REMOVE

    def __on_override__(self, overriden):
        self.shared.setdefault("override", []).append((self, overriden))

    def __on_overridden__(self, override):
        self.shared.setdefault("overridden", []).append((self, override))


def test_descriptors():
    shared = {}
    foo_descriptor = SlotDescriptor(shared)
    bar_descriptor = SlotDescriptor(shared)

    class StuffMeta(OwnerMeta, GenericMeta):
        pass

    class Stuff(with_metaclass(StuffMeta, Owner, Generic[T])):
        foo = foo_descriptor
        bar = bar_descriptor

        assert not foo.named
        assert not foo.owned

        assert not bar.named
        assert not bar.owned

    assert "foo" in Stuff.__slots__
    assert "bar" in Stuff.__slots__

    assert foo_descriptor.named
    assert foo_descriptor.owned

    assert bar_descriptor.named
    assert bar_descriptor.owned

    assert foo_descriptor.name == "foo"
    assert bar_descriptor.name == "bar"

    assert foo_descriptor.owner is Stuff
    assert bar_descriptor.owner is Stuff

    descriptors = collections.OrderedDict()
    descriptors["foo"] = foo_descriptor
    descriptors["bar"] = bar_descriptor
    assert get_descriptors(Stuff) == MappingProxyType(descriptors)

    new_foo_descriptor = SlotDescriptor(shared)

    class StuffOverride(Stuff[int]):
        foo = new_foo_descriptor

    assert new_foo_descriptor.name == "foo"
    assert new_foo_descriptor.owner is StuffOverride

    assert shared == {
        "override": [(new_foo_descriptor, foo_descriptor)],
        "overridden": [(foo_descriptor, new_foo_descriptor)],
    }

    new_descriptors = collections.OrderedDict()
    new_descriptors["foo"] = new_foo_descriptor
    new_descriptors["bar"] = bar_descriptor
    assert get_descriptors(StuffOverride) == MappingProxyType(new_descriptors)

    foobar_descriptor = SlotDescriptor(shared, priority=0)

    class StuffWithPrio(StuffOverride):
        foobar = foobar_descriptor

    assert foobar_descriptor.name == "foobar"
    assert foobar_descriptor.owner is StuffWithPrio

    prio_descriptors = collections.OrderedDict()
    prio_descriptors["foobar"] = foobar_descriptor
    prio_descriptors["foo"] = new_foo_descriptor
    prio_descriptors["bar"] = bar_descriptor
    assert get_descriptors(StuffWithPrio) == MappingProxyType(prio_descriptors)

    this_descriptors_a = collections.OrderedDict()
    this_descriptors_a["foo"] = foo_descriptor
    this_descriptors_a["bar"] = bar_descriptor
    assert get_descriptors(Stuff, inherited=False) == MappingProxyType(
        this_descriptors_a
    )

    this_descriptors_b = collections.OrderedDict()
    this_descriptors_b["foo"] = new_foo_descriptor
    assert get_descriptors(StuffOverride, inherited=False) == MappingProxyType(
        this_descriptors_b
    )

    this_descriptors_c = collections.OrderedDict()
    this_descriptors_c["foobar"] = foobar_descriptor
    assert get_descriptors(StuffWithPrio, inherited=False) == MappingProxyType(
        this_descriptors_c
    )


def test_bad_override():
    shared = {}

    class Stuff(Owner):
        foo = SlotDescriptor(shared)
        bar = SlotDescriptor(shared)

    with pytest.raises(TypeError):

        class BadStuff(Stuff):  # noqa
            foo = 3


def test_required_slots():
    shared = {}

    class Stuff(Owner):
        foo = SlotDescriptor(shared)
        bar = SlotDescriptor(shared)

    class MoreStuff(Stuff):
        foo = SlotDescriptor(shared)
        foobar = SlotDescriptor(shared)

    assert Stuff.__slots__ == ("foo", "bar")
    assert MoreStuff.__slots__ == ("foobar",)


def test_with_bases():
    shared = {}

    class StructMeta(CompatBaseMeta, OwnerMeta):
        pass

    class Struct(with_metaclass(StructMeta, CompatBase, Owner, Generic[T])):
        __slots__ = ()

    class Point(Struct):
        x = SlotDescriptor(shared)
        y = SlotDescriptor(shared)

    assert Point
    assert not getattr(Struct, "_OwnerMeta__this_descriptors")
    assert len(getattr(Point, "_OwnerMeta__this_descriptors")) == 2


if __name__ == "__main__":
    pytest.main()
