import pytest  # noqa

from basicco.fabricate_value import fabricate_value, format_factory


def test_fabricate_value():
    assert fabricate_value(None, 3) == 3
    assert fabricate_value(str, 3) == "3"
    assert fabricate_value("str", 3) == "3"


def test_format_factory():
    assert format_factory(None) is None
    assert format_factory(str) is str
    assert format_factory("str") == "str"

    with pytest.raises(TypeError):
        format_factory(3)  # type: ignore


if __name__ == "__main__":
    pytest.main()
