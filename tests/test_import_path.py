import itertools
import math

import pytest

from basicco.import_path import get_path, import_path, extract_generic_paths


class MyClass:
    class MyNestedClass:
        pass


def test_import_path():
    assert import_path("math.floor") is math.floor
    assert import_path("itertools.chain") is itertools.chain
    assert import_path(__name__ + ".MyClass") is MyClass
    assert import_path(__name__ + ".MyClass.MyNestedClass") is MyClass.MyNestedClass

    with pytest.raises(ImportError):
        import_path("module.submodule.<locals>.Test")


def test_get_path():
    assert get_path(math.floor) == "math.floor"
    assert get_path(itertools.chain) == "itertools.chain"
    assert get_path(MyClass) == __name__ + ".MyClass"
    assert get_path(MyClass.MyNestedClass) == __name__ + ".MyClass.MyNestedClass"

    class LocalClass:
        pass

    with pytest.raises(AttributeError):
        get_path(LocalClass)


def test_extract_generic_paths():
    assert extract_generic_paths("Tuple[int, str]") == ("Tuple", ("int", "str"))


if __name__ == "__main__":
    pytest.main()
