from pickle import loads, dumps

from pytest import main, raises

from basicco.utils.wrapped_dict import WrappedDict


def test_wrapped_dict():
    wrapped = {"bar": "foo"}
    wrapped = WrappedDict(wrapped)
    assert dict(wrapped) == {"bar": "foo"}
    assert wrapped == {"bar": "foo"}

    assert wrapped.clear() == WrappedDict()
    assert wrapped.copy() == WrappedDict({"bar": "foo"})
    assert wrapped.set("foo", "bar") == WrappedDict({"bar": "foo", "foo": "bar"})
    assert wrapped.update({"foo": "bar"}) == WrappedDict({"bar": "foo", "foo": "bar"})
    assert wrapped.update({"bar": "baz"}, foo="bar") == WrappedDict(
        {"bar": "baz", "foo": "bar"}
    )
    assert wrapped.update(foo="bar") == WrappedDict({"bar": "foo", "foo": "bar"})
    assert wrapped.delete("bar") == WrappedDict()
    assert wrapped.discard("baz") == wrapped

    with raises(KeyError):
        wrapped.delete("baz")

    with raises(AttributeError):
        wrapped.foo = "bar"

    with raises(AttributeError):
        del wrapped.foo


def test_pickle():
    wrapped = {"bar": "foo"}
    wrapped = WrappedDict(wrapped)
    assert loads(dumps(wrapped)) == wrapped
    assert loads(dumps(wrapped)) == wrapped


if __name__ == "__main__":
    main()
