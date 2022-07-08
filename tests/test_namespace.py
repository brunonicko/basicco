from __future__ import absolute_import, division, print_function

from pickle import loads, dumps

import six
from pytest import main

from basicco.namespace import _WRAPPED_SLOT, Namespace, MutableNamespace, NamespacedMeta


def test_read_only_namespace():
    wrapped = {"update": "foo"}
    ns = Namespace(wrapped)
    assert hasattr(ns, _WRAPPED_SLOT)
    assert getattr(ns, _WRAPPED_SLOT) is wrapped
    assert dict(ns) == {"update": "foo"}

    assert hasattr(ns, "update")
    assert ns.update == "foo"


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

    del ns.update
    assert not hasattr(ns, "update")

    ns.update = "foo"
    assert hasattr(ns, "update")
    assert ns.update == "foo"

    ns.update = "bar"
    assert hasattr(ns, "update")
    assert ns.update == "bar"

    del ns.update
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


def test_private_namespace():
    class Class(six.with_metaclass(NamespacedMeta)):
        pass

    assert isinstance(Class.__namespace__, MutableNamespace)

    class SubClassA(Class):
        pass

    assert isinstance(SubClassA.__namespace__, MutableNamespace)

    class SubClassB(Class):
        pass

    assert isinstance(SubClassB.__namespace__, MutableNamespace)

    class SubClassC(SubClassA, SubClassB):
        pass

    assert isinstance(SubClassC.__namespace__, MutableNamespace)

    namespace_ids = {
        id(Class.__namespace__),
        id(SubClassA.__namespace__),
        id(SubClassB.__namespace__),
        id(SubClassC.__namespace__),
    }

    assert len(namespace_ids) == 4


if __name__ == "__main__":
    main()
