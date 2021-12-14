from pytest import main

from basicco.utils.private_naming import privatize_name, deprivatize_name


def test_privatize_name():
    assert privatize_name("Foo", "bar") == "bar"
    assert privatize_name("Foo", "_bar") == "_bar"
    assert privatize_name("Foo", "__bar__") == "__bar__"
    assert privatize_name("Foo", "__bar") == "_Foo__bar"
    assert privatize_name("_Foo", "__bar") == "_Foo__bar"
    assert privatize_name("__Foo", "__bar") == "_Foo__bar"


def test_deprivatize_name():
    assert deprivatize_name("bar") == ("bar", None)
    assert deprivatize_name("_bar") == ("_bar", None)
    assert deprivatize_name("__bar__") == ("__bar__", None)
    assert deprivatize_name("_Foo_bar") == ("_Foo_bar", None)
    assert deprivatize_name("_Foo__bar__") == ("_Foo__bar__", None)
    assert deprivatize_name("_Foo__bar") == ("__bar", "Foo")


if __name__ == "__main__":
    main()
