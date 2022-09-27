from pickle import dumps, loads

import pytest  # noqa
import six

from basicco.namespace import _WRAPPED_SLOT  # noqa
from basicco.namespace import MutableNamespace, Namespace, Namespaced, NamespacedMeta


def test_read_only_namespace():
    wrapped = {"update": "foo"}
    ns = Namespace(wrapped)
    assert hasattr(ns, _WRAPPED_SLOT)
    assert getattr(ns, _WRAPPED_SLOT) is wrapped
    assert dict(ns) == {"update": "foo"}

    assert hasattr(ns, "update")
    assert ns.update == "foo"
    assert ns["update"] == "foo"


def test_pickle():
    wrapped = {"update": "foo"}
    rns = Namespace(wrapped)
    ns = MutableNamespace(wrapped)

    assert loads(dumps(rns)) == rns
    assert loads(dumps(ns)) == ns


def test_namespace():
    wrapped = {"update": "foo"}
    ns = MutableNamespace(wrapped)

    ns.update = "bar"
    assert hasattr(ns, "update")
    assert ns.update == "bar"
    assert ns["update"] == "bar"

    del ns.update
    assert not hasattr(ns, "update")

    ns.update = "foo"
    assert hasattr(ns, "update")
    assert ns.update == "foo"
    assert ns["update"] == "foo"

    ns.update = "bar"
    assert hasattr(ns, "update")
    assert ns.update == "bar"
    assert ns["update"] == "bar"

    del ns["update"]
    assert not hasattr(ns, "update")


def test_wrap_mutable_namespace():
    mns = MutableNamespace({"foo": "bar"})
    ns = Namespace(mns)
    assert hasattr(mns, "foo")
    assert hasattr(ns, "foo")

    mns.bar = "foo"
    assert hasattr(mns, "bar")
    assert hasattr(ns, "bar")


def test_wrap_namespace():
    ns = Namespace({"foo": "bar"})
    mns = MutableNamespace(ns)
    assert hasattr(ns, "foo")
    assert hasattr(mns, "foo")

    mns.bar = "foo"
    assert hasattr(mns, "bar")
    assert hasattr(ns, "bar")


def test_class():
    assert isinstance(Namespaced, NamespacedMeta)


def test_metaclass():
    class Class(six.with_metaclass(NamespacedMeta, object)):
        @classmethod
        def set_class_value(cls, value):
            cls.__namespace.value = value

        @classmethod
        def get_class_value(cls):
            return cls.__namespace.value

    Class.set_class_value("foobar")
    assert Class.get_class_value() == "foobar"


def test_metaclass_uniqueness():
    class Class(six.with_metaclass(NamespacedMeta)):
        @classmethod
        def get_namespace(cls):
            return cls.__namespace

    assert isinstance(Class.get_namespace(), MutableNamespace)

    class SubClassA(Class):
        @classmethod
        def get_namespace(cls):
            return cls.__namespace

    assert isinstance(SubClassA.get_namespace(), MutableNamespace)

    class SubClassB(Class):
        @classmethod
        def get_namespace(cls):
            return cls.__namespace

    assert isinstance(SubClassB.get_namespace(), MutableNamespace)

    class SubClassC(SubClassA, SubClassB):
        @classmethod
        def get_namespace(cls):
            return cls.__namespace

    assert isinstance(SubClassC.get_namespace(), MutableNamespace)

    namespace_ids = {
        id(Class.get_namespace()),
        id(SubClassA.get_namespace()),
        id(SubClassB.get_namespace()),
        id(SubClassC.get_namespace()),
    }

    assert len(namespace_ids) == 4


if __name__ == "__main__":
    pytest.main()
