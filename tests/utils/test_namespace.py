from pickle import loads, dumps

from pytest import main

from basicco.utils.namespace import _WRAPPED, ReadOnlyNamespace, Namespace


def test_read_only_namespace():
    wrapped = {"update": "foo"}
    ns = ReadOnlyNamespace(wrapped)
    assert hasattr(ns, _WRAPPED)
    assert getattr(ns, _WRAPPED) is wrapped
    assert dict(ns) == {"update": "foo"}

    assert hasattr(ns, "update")
    assert ns.update == "foo"


def test_pickle():
    wrapped = {"update": "foo"}
    rns = ReadOnlyNamespace(wrapped)
    ns = Namespace(wrapped)

    assert loads(dumps(rns)) == rns
    assert loads(dumps(ns)) == ns


def test_namespace():
    wrapped = {"update": "foo"}
    ns = Namespace(wrapped)

    ns.update = "bar"
    assert hasattr(ns, "update")
    assert ns.update == "bar"

    del ns.update
    assert not hasattr(ns, "update")

    ns["update"] = "foo"
    assert hasattr(ns, "update")
    assert ns.update == "foo"

    ns["update"] = "bar"
    assert hasattr(ns, "update")
    assert ns.update == "bar"

    del ns["update"]
    assert not hasattr(ns, "update")


def test_wrap_namespace():
    ns = Namespace({"foo": "bar"})
    rns = ReadOnlyNamespace(ns)
    assert hasattr(ns, "foo")
    assert hasattr(rns, "foo")

    ns.bar = "foo"
    assert hasattr(ns, "bar")
    assert hasattr(rns, "bar")


def test_wrap_read_only_namespace():
    rns = ReadOnlyNamespace({"foo": "bar"})
    ns = Namespace(rns)
    assert hasattr(rns, "foo")
    assert hasattr(ns, "foo")

    ns.bar = "foo"
    assert hasattr(ns, "bar")
    assert not hasattr(rns, "bar")


if __name__ == "__main__":
    main()
