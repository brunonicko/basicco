import collections
import itertools
import math

import pytest  # noqa
import six.moves
import tippo

from basicco.import_path import extract_generic_paths, get_path, import_path


class MyClass(object):
    class MyNestedClass(object):
        pass


def test_import_path():
    assert import_path("math.floor") is math.floor
    assert import_path("itertools.chain") is itertools.chain
    assert import_path("six.moves") is six.moves
    assert import_path("six.moves.collections_abc") is six.moves.collections_abc  # type: ignore

    assert import_path(__name__ + ".MyClass") is MyClass
    assert import_path(__name__ + ".MyClass.MyNestedClass") is MyClass.MyNestedClass

    with pytest.raises(ImportError):
        import_path("module.submodule.<locals>.Test")


def test_get_path():
    assert get_path(math.floor) == "math.floor"
    assert get_path(itertools.chain) == "itertools.chain"
    assert get_path(six.moves) == "six.moves"

    assert get_path(MyClass) == __name__ + ".MyClass"
    assert get_path(MyClass.MyNestedClass) == __name__ + ".MyClass.MyNestedClass"

    assert get_path(tippo.Mapping[str, int]) == "typing.Mapping[str, int]"

    if hasattr(collections, "abc"):
        col_mapping = six.moves.collections_abc.Mapping  # type: ignore
        try:
            typed_col_mapping = col_mapping[str, int]
        except TypeError:
            pass
        else:
            assert get_path(typed_col_mapping) == "collections.abc.Mapping[str, int]"

    class LocalClass(object):
        pass

    with pytest.raises(ImportError):
        get_path(LocalClass)

    objs = (tippo.Mapping[str, int], MyClass, "MyClass", "Mapping[str, int]")
    for obj in objs:
        path = get_path(obj)
        assert import_path(path) == obj


def test_extract_generic_paths():
    assert extract_generic_paths("Tuple[int, str]") == ("Tuple", ("int", "str"))


if __name__ == "__main__":
    pytest.main()
