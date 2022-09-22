import abc
import itertools

import pytest  # noqa
import tippo

from basicco.type_checking import (
    TypeCheckError,
    assert_is_callable,
    assert_is_instance,
    assert_is_iterable,
    assert_is_subclass,
    format_types,
    import_types,
    is_instance,
    is_iterable,
    is_subclass,
    type_names,
)


class Cls(object):
    pass


class SubCls(Cls):
    pass


class Parent(object):
    class Child(object):
        pass


cls_path = __name__ + "." + Cls.__name__
subcls_path = __name__ + "." + SubCls.__name__
nested_cls_path = __name__ + "." + Parent.__name__ + "." + Parent.Child.__name__


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
    with pytest.raises(TypeCheckError):
        assert_is_instance(0, None)
        assert_is_instance(0, (None,))

    assert_is_instance(Cls(), cls_path)
    assert_is_instance(Cls(), cls_path, subtypes=False)
    assert_is_instance(SubCls(), cls_path)

    with pytest.raises(TypeCheckError):
        assert_is_instance(SubCls(), cls_path, subtypes=False)

    assert_is_instance(SubCls(), subcls_path, subtypes=False)

    assert_is_instance(Cls(), (cls_path, Cls, int))
    assert_is_instance(Cls(), (cls_path, Cls, int), subtypes=False)
    assert_is_instance(SubCls(), (cls_path, Cls, int))

    with pytest.raises(TypeCheckError):
        assert_is_instance(SubCls(), (cls_path, Cls, int), subtypes=False)

    assert_is_instance(SubCls(), (subcls_path, SubCls, int), subtypes=False)

    with pytest.raises(TypeCheckError):
        assert_is_instance(Cls(), (int, float))

    with pytest.raises(TypeCheckError):
        assert_is_instance(Cls(), (int, float), subtypes=False)

    with pytest.raises(TypeCheckError):
        assert_is_instance(SubCls(), (int, float))

    with pytest.raises(TypeCheckError):
        assert_is_instance(SubCls(), (int, float), subtypes=False)

    with pytest.raises(TypeCheckError):
        assert_is_instance(SubCls(), (int, float), subtypes=False)

    with pytest.raises(ValueError):
        assert_is_instance(Cls(), ())

    with pytest.raises(ValueError):
        assert_is_instance(SubCls(), ())


def test_assert_is_subclass():
    assert_is_subclass(type(None), None)
    assert_is_subclass(type(None), (None,))
    with pytest.raises(TypeCheckError):
        assert_is_subclass(int, None)
        assert_is_subclass(int, (None,))

    assert_is_subclass(Cls, cls_path)
    assert_is_subclass(Cls, cls_path, subtypes=False)
    assert_is_subclass(SubCls, cls_path)

    with pytest.raises(TypeCheckError):
        assert_is_subclass(SubCls, cls_path, subtypes=False)

    assert_is_subclass(SubCls, subcls_path, subtypes=False)

    assert_is_subclass(Cls, (cls_path, Cls, int))
    assert_is_subclass(Cls, (cls_path, Cls, int), subtypes=False)
    assert_is_subclass(SubCls, (cls_path, Cls, int))

    with pytest.raises(TypeCheckError):
        assert_is_subclass(SubCls, (cls_path, Cls, int), subtypes=False)

    assert_is_subclass(SubCls, (subcls_path, SubCls, int), subtypes=False)

    with pytest.raises(TypeCheckError):
        assert_is_subclass(Cls, (int, float))  # type: ignore

    with pytest.raises(TypeCheckError):
        assert_is_subclass(Cls, (int, float), subtypes=False)  # type: ignore

    with pytest.raises(TypeCheckError):
        assert_is_subclass(SubCls, (int, float))  # type: ignore

    with pytest.raises(TypeCheckError):
        assert_is_subclass(SubCls, (int, float), subtypes=False)  # type: ignore

    with pytest.raises(TypeCheckError):
        assert_is_subclass(SubCls, (int, float), subtypes=False)  # type: ignore

    with pytest.raises(ValueError):
        assert_is_subclass(Cls, ())

    with pytest.raises(ValueError):
        assert_is_subclass(SubCls, ())


def test_assert_is_callable():
    assert_is_callable(int)

    with pytest.raises(TypeCheckError):
        assert_is_callable(3)  # type: ignore


def test_assert_is_iterable():
    with pytest.raises(TypeCheckError):
        assert_is_iterable(3)  # type: ignore

    with pytest.raises(TypeCheckError):
        assert_is_iterable(False)  # type: ignore

    with pytest.raises(TypeCheckError):
        assert_is_iterable("foo")

    assert_is_iterable("foo", include_strings=True)

    assert_is_iterable([])
    assert_is_iterable({})
    assert_is_iterable(set())


def test_typing_type():
    assert is_instance(3.0, float) == isinstance(3.0, float)
    assert is_instance(float, tippo.Type[float]) == is_subclass(float, float)

    assert is_subclass(float, tippo.Type[tippo.Type[float]]) == is_subclass(float, type(float))
    assert is_subclass(float, tippo.Type[int]) == is_subclass(float, type)

    assert is_instance({"a": 1}, tippo.Mapping[str, int])
    assert is_instance({"a": 1}, tippo.Dict[str, int])
    assert is_instance(["a"], tippo.Iterable[str])
    assert is_instance(["a"], tippo.List[str])
    assert is_instance({"a"}, tippo.Iterable[str])
    assert is_instance({"a"}, tippo.Set[str])

    assert not is_instance({"a": 1}, tippo.Mapping[float, str])
    assert not is_instance({"a": 1}, tippo.Dict[float, str])
    assert not is_instance(["a"], tippo.Iterable[int])
    assert not is_instance(["a"], tippo.List[int])
    assert not is_instance({"a"}, tippo.Iterable[int])
    assert not is_instance({"a"}, tippo.Set[int])

    assert is_instance(dict, tippo.Type[tippo.Mapping])
    assert is_instance(dict, tippo.Type[tippo.Dict])
    assert is_instance(list, tippo.Type[tippo.Iterable])
    assert is_instance(list, tippo.Type[tippo.List])
    assert is_instance(set, tippo.Type[tippo.Iterable])
    assert is_instance(set, tippo.Type[tippo.Set])

    assert is_instance(dict, tippo.Type[tippo.Mapping[int, str]])
    assert is_instance(dict, tippo.Type[tippo.Dict[int, str]])
    assert is_instance(list, tippo.Type[tippo.Iterable[int]])
    assert is_instance(list, tippo.Type[tippo.List[int]])
    assert is_instance(set, tippo.Type[tippo.Iterable[int]])
    assert is_instance(set, tippo.Type[tippo.Set[int]])

    assert is_instance(3, tippo.Any)
    assert is_instance(True, tippo.Literal[True, False])
    assert is_instance(3, tippo.Union[int, str])
    assert is_instance(int, tippo.Type[int])
    assert is_instance((3, "3"), tippo.Tuple[int, str])
    assert is_instance((3, 4, 5), tippo.Tuple[int, ...])
    assert is_instance({"3": 3}, tippo.Mapping[str, int])
    assert is_instance([1, 2, 3], tippo.Iterable[int])

    assert not is_instance(None, tippo.Literal[True, False])
    assert not is_instance(3.4, tippo.Union[int, str])
    assert not is_instance(float, tippo.Type[int])
    assert not is_instance(("3", 3), tippo.Tuple[int, str])
    assert not is_instance(("3", "4", "5"), tippo.Tuple[int, ...])
    assert not is_instance({3: "3"}, tippo.Mapping[str, int])
    assert not is_instance([1, 2, 3], tippo.Iterable[str])

    assert is_instance(Parent.Child(), tippo.Optional[nested_cls_path])


if __name__ == "__main__":
    pytest.main()
