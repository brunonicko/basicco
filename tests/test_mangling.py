import pytest  # noqa

from basicco.mangling import extract, mangle, unmangle


def test_mangle():
    assert mangle("bar", "Foo") == "bar"
    assert mangle("_bar", "Foo") == "_bar"
    assert mangle("__bar__", "Foo") == "__bar__"
    assert mangle("__bar", "Foo") == "_Foo__bar"
    assert mangle("__bar", "_Foo") == "_Foo__bar"
    assert mangle("__bar", "__Foo") == "_Foo__bar"


def test_unmangle():
    assert unmangle("bar", "Foo") == "bar"
    assert unmangle("_bar", "Foo") == "_bar"
    assert unmangle("__bar__", "Foo") == "__bar__"
    assert unmangle("_Foo_bar", "Foo") == "_Foo_bar"
    assert unmangle("_Foo__bar__", "Foo") == "_Foo__bar__"
    assert unmangle("_Foo__bar", "Foo") == "__bar"


def test_extract():
    assert extract("bar") == ("bar", None)
    assert extract("_bar") == ("_bar", None)
    assert extract("__bar__") == ("__bar__", None)
    assert extract("_Foo_bar") == ("_Foo_bar", None)
    assert extract("_Foo__bar__") == ("_Foo__bar__", None)
    assert extract("_Foo__bar") == ("__bar", "Foo")


if __name__ == "__main__":
    pytest.main()
