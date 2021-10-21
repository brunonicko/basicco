import pytest
import typing

from six import with_metaclass

from basicco.generic import GenericMeta

T = typing.TypeVar("T")


def test_generic():
    class Class(with_metaclass(GenericMeta, object)):
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
