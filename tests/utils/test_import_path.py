from itertools import chain
from math import floor

import pytest

from basicco.utils.import_path import (
    format_import_path,
    get_import_path,
    import_from_path,
)


class MyClass(object):
    class MyNestedClass(object):
        pass


def test_import_from_path():
    assert import_from_path("math|floor") is floor
    assert import_from_path("itertools|chain") is chain
    assert import_from_path(__name__ + "|MyClass") is MyClass
    assert (
        import_from_path(__name__ + "|MyClass.MyNestedClass") is MyClass.MyNestedClass
    )

    with pytest.raises(ValueError):
        import_from_path("module.submodule|<locals>.Test")


def test_get_import_path():
    assert get_import_path(floor) == "math|floor"
    assert get_import_path(chain) == "itertools|chain"
    assert get_import_path(MyClass) == __name__ + "|MyClass"
    assert get_import_path(MyClass.MyNestedClass) == __name__ + "|MyClass.MyNestedClass"

    class LocalClass(object):
        pass

    with pytest.raises(AttributeError):
        get_import_path(LocalClass)


def test_format_import_path():
    assert format_import_path("abstractmethod", "abc") == "abc|abstractmethod"
    assert format_import_path(".abstractmethod", "abc") == "abc|abstractmethod"
    assert format_import_path("abc|abstractmethod", "") == "abc|abstractmethod"
    assert format_import_path("..Mapping", "collections.abc") == "collections|Mapping"
    assert (
        format_import_path(".Mapping", "collections.abc") == "collections.abc|Mapping"
    )

    with pytest.raises(ValueError):
        format_import_path("abstract method|a b c", "xyz")

    with pytest.raises(ValueError):
        format_import_path("abstract method", "abc")

    with pytest.raises(ValueError):
        format_import_path("abstractmethod", "a b c")

    assert format_import_path("..Counter", "collections.abc") == "collections|Counter"
    assert format_import_path("..listdir", "os.path") == "os|listdir"


if __name__ == "__main__":
    pytest.main()
