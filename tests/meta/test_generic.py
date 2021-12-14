import pytest
import typing

from six import with_metaclass

from basicco.generic import GenericMeta

T = typing.TypeVar("T")


@pytest.fixture()
def meta(pytestconfig):
    metacls = pytestconfig.getoption("metacls")
    if metacls:
        meta_module, meta_name = metacls.split("|")
        return getattr(__import__(meta_module, fromlist=[meta_name]), meta_name)
    else:
        return GenericMeta


def test_generic(meta):
    class Class(with_metaclass(meta, object)):
        pass

    # Bracket syntax should not work if class doesn't inherit from Generic.
    with pytest.raises(TypeError):
        _BadClass = Class[None]  # type: ignore
        assert not _BadClass

    # Should error if didn't specify type variables to Generic.
    with pytest.raises(TypeError):

        class _BadClass(Class, typing.Generic[3]):  # type: ignore
            pass

        assert not _BadClass

    with pytest.raises(TypeError):

        class _BadClass(Class, typing.Generic[int]):  # type: ignore
            pass

        assert not _BadClass

    # Declare a proper Generic class and check inheritance, equality, and instantiation.
    class _Class(Class, typing.Generic[T]):
        pass

    assert issubclass(_Class, Class)
    assert _Class[int]
    assert (_Class[int] == _Class[int]) is True
    assert (_Class[int] == _Class[(int,)]) is True
    assert (_Class[int] != _Class[(int,)]) is False

    assert isinstance(_Class[int](), _Class)
    assert isinstance(
        _Class[(int,)](),
        _Class,
    )


if __name__ == "__main__":
    pytest.main()
