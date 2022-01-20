import pytest

from basicco.utils.value_factoring import (
    format_factory,
    import_factory,
    fabricate_value,
)


def test_format_factory():
    assert format_factory(None) is None
    assert format_factory(str) is str
    assert format_factory("str") == "str"


def test_import_factory():
    assert import_factory(None) is None
    assert import_factory(str) is str
    assert import_factory("str") is str


def test_fabricate_value():
    assert fabricate_value(None, 3) == 3
    assert fabricate_value(str, 3) == "3"
    assert fabricate_value("str", 3) == "3"


if __name__ == "__main__":
    pytest.main()
