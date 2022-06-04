from pytest import main

from basicco.privatize import privatize, deprivatize


def test_privatize():
    assert privatize("bar", "Foo") == "bar"
    assert privatize("_bar", "Foo") == "_bar"
    assert privatize("__bar__", "Foo") == "__bar__"
    assert privatize("__bar", "Foo") == "_Foo__bar"
    assert privatize("__bar", "_Foo") == "_Foo__bar"
    assert privatize("__bar", "__Foo") == "_Foo__bar"


def test_deprivatize():
    assert deprivatize("bar") == ("bar", None)
    assert deprivatize("_bar") == ("_bar", None)
    assert deprivatize("__bar__") == ("__bar__", None)
    assert deprivatize("_Foo_bar") == ("_Foo_bar", None)
    assert deprivatize("_Foo__bar__") == ("_Foo__bar__", None)
    assert deprivatize("_Foo__bar") == ("__bar", "Foo")


if __name__ == "__main__":
    main()
