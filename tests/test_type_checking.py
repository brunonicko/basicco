from __future__ import absolute_import, division, print_function

import abc
import itertools

import pytest

from basicco.type_checking import (
    assert_is_callable,
    assert_is_instance,
    assert_is_subclass,
    assert_is_iterable,
    is_iterable,
    format_types,
    type_names,
    import_types,
    is_instance,
    is_subclass,
)


class Cls(object):
    pass


class SubCls(Cls):
    pass


cls_path = __name__ + "." + Cls.__name__
subcls_path = __name__ + "." + SubCls.__name__


def test_format_types():
    assert format_types(None) == (type(None),)
    assert format_types((None,)) == (type(None),)
    assert format_types(float) == (float,)
    assert format_types("itertools.chain") == ("itertools.chain",)
    with pytest.raises(TypeError):
        format_types(3)  # type: ignore


def test_type_names():
    assert type_names(None) == (type(None).__name__,)
    assert type_names((None,)) == (type(None).__name__,)
    assert type_names(("module.module.Cls", "abc.abstractmethod", abc.ABCMeta, itertools.chain)) == (
        "Cls",
        "abstractmethod",
        "ABCMeta",
        "chain",
    )


def test_import_types():
    assert import_types(None) == (type(None),)
    assert import_types((None,)) == (type(None),)
    assert import_types(("abc.abstractmethod", abc.ABCMeta, itertools.chain)) == (
        abc.abstractmethod,
        abc.ABCMeta,
        itertools.chain,
    )


def test_is_instance():
    assert is_instance(None, None)
    assert is_instance(None, (None,))
    assert not is_instance(0, None)
    assert not is_instance(0, (None,))

    assert is_instance(Cls(), cls_path) is True
    assert is_instance(Cls(), cls_path, subtypes=False) is True
    assert is_instance(SubCls(), cls_path) is True
    assert is_instance(SubCls(), cls_path, subtypes=False) is False
    assert is_instance(SubCls(), subcls_path, subtypes=False) is True

    assert is_instance(Cls(), (cls_path, Cls, int)) is True
    assert is_instance(Cls(), (cls_path, Cls, int), subtypes=False) is True
    assert is_instance(SubCls(), (cls_path, Cls, int)) is True
    assert is_instance(SubCls(), (cls_path, Cls, int), subtypes=False) is False
    assert is_instance(SubCls(), (subcls_path, SubCls, int), subtypes=False) is True

    assert is_instance(Cls(), (int, float)) is False
    assert is_instance(Cls(), (int, float), subtypes=False) is False
    assert is_instance(SubCls(), (int, float)) is False
    assert is_instance(SubCls(), (int, float), subtypes=False) is False
    assert is_instance(SubCls(), (int, float), subtypes=False) is False

    assert is_instance(Cls(), ()) is False
    assert is_instance(SubCls(), ()) is False


def test_is_subclass():
    assert is_subclass(type(None), None)
    assert is_subclass(type(None), (None,))
    assert not is_subclass(int, None)
    assert not is_subclass(int, (None,))

    assert is_subclass(Cls, cls_path) is True
    assert is_subclass(Cls, cls_path, subtypes=False) is True
    assert is_subclass(SubCls, cls_path) is True
    assert is_subclass(SubCls, cls_path, subtypes=False) is False
    assert is_subclass(SubCls, subcls_path, subtypes=False) is True

    assert is_subclass(Cls, (cls_path, Cls, int)) is True
    assert is_subclass(Cls, (cls_path, Cls, int), subtypes=False) is True
    assert is_subclass(SubCls, (cls_path, Cls, int)) is True
    assert is_subclass(SubCls, (cls_path, Cls, int), subtypes=False) is False
    assert is_subclass(SubCls, (subcls_path, SubCls, int), subtypes=False) is True

    assert is_subclass(Cls, (int, float)) is False
    assert is_subclass(Cls, (int, float), subtypes=False) is False
    assert is_subclass(SubCls, (int, float)) is False
    assert is_subclass(SubCls, (int, float), subtypes=False) is False
    assert is_subclass(SubCls, (int, float), subtypes=False) is False

    assert is_subclass(Cls, ()) is False
    assert is_subclass(SubCls, ()) is False


def test_is_iterable():
    assert not is_iterable(3)
    assert not is_iterable(False)
    assert not is_iterable("foo")

    assert is_iterable("foo", include_strings=True)
    assert is_iterable([])
    assert is_iterable({})
    assert is_iterable(set())


def test_assert_is_instance():
    assert_is_instance(None, None)
    assert_is_instance(None, (None,))
    with pytest.raises(TypeError):
        assert_is_instance(0, None)
        assert_is_instance(0, (None,))

    assert_is_instance(Cls(), cls_path)
    assert_is_instance(Cls(), cls_path, subtypes=False)
    assert_is_instance(SubCls(), cls_path)

    with pytest.raises(TypeError):
        assert_is_instance(SubCls(), cls_path, subtypes=False)

    assert_is_instance(SubCls(), subcls_path, subtypes=False)

    assert_is_instance(Cls(), (cls_path, Cls, int))
    assert_is_instance(Cls(), (cls_path, Cls, int), subtypes=False)
    assert_is_instance(SubCls(), (cls_path, Cls, int))

    with pytest.raises(TypeError):
        assert_is_instance(SubCls(), (cls_path, Cls, int), subtypes=False)

    assert_is_instance(SubCls(), (subcls_path, SubCls, int), subtypes=False)

    with pytest.raises(TypeError):
        assert_is_instance(Cls(), (int, float))

    with pytest.raises(TypeError):
        assert_is_instance(Cls(), (int, float), subtypes=False)

    with pytest.raises(TypeError):
        assert_is_instance(SubCls(), (int, float))

    with pytest.raises(TypeError):
        assert_is_instance(SubCls(), (int, float), subtypes=False)

    with pytest.raises(TypeError):
        assert_is_instance(SubCls(), (int, float), subtypes=False)

    with pytest.raises(ValueError):
        assert_is_instance(Cls(), ())

    with pytest.raises(ValueError):
        assert_is_instance(SubCls(), ())


def test_assert_is_subclass():
    assert_is_subclass(type(None), None)
    assert_is_subclass(type(None), (None,))
    with pytest.raises(TypeError):
        assert_is_subclass(int, None)
        assert_is_subclass(int, (None,))

    assert_is_subclass(Cls, cls_path)
    assert_is_subclass(Cls, cls_path, subtypes=False)
    assert_is_subclass(SubCls, cls_path)

    with pytest.raises(TypeError):
        assert_is_subclass(SubCls, cls_path, subtypes=False)

    assert_is_subclass(SubCls, subcls_path, subtypes=False)

    assert_is_subclass(Cls, (cls_path, Cls, int))
    assert_is_subclass(Cls, (cls_path, Cls, int), subtypes=False)
    assert_is_subclass(SubCls, (cls_path, Cls, int))

    with pytest.raises(TypeError):
        assert_is_subclass(SubCls, (cls_path, Cls, int), subtypes=False)

    assert_is_subclass(SubCls, (subcls_path, SubCls, int), subtypes=False)

    with pytest.raises(TypeError):
        assert_is_subclass(Cls, (int, float))

    with pytest.raises(TypeError):
        assert_is_subclass(Cls, (int, float), subtypes=False)

    with pytest.raises(TypeError):
        assert_is_subclass(SubCls, (int, float))

    with pytest.raises(TypeError):
        assert_is_subclass(SubCls, (int, float), subtypes=False)

    with pytest.raises(TypeError):
        assert_is_subclass(SubCls, (int, float), subtypes=False)

    with pytest.raises(ValueError):
        assert_is_subclass(Cls, ())

    with pytest.raises(ValueError):
        assert_is_subclass(SubCls, ())


def test_assert_is_callable():
    assert_is_callable(int)

    with pytest.raises(TypeError):
        assert_is_callable(3)


def test_assert_is_iterable():
    with pytest.raises(TypeError):
        assert_is_iterable(3)

    with pytest.raises(TypeError):
        assert_is_iterable(False)

    with pytest.raises(TypeError):
        assert_is_iterable("foo")

    assert_is_iterable("foo", include_strings=True)

    assert_is_iterable([])
    assert_is_iterable({})
    assert_is_iterable(set())


if __name__ == "__main__":
    pytest.main()
