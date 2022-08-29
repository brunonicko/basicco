import pytest

from six import with_metaclass
from tippo import TypeVar, Generic

from basicco.generic_meta import GenericMeta


T = TypeVar("T")


def test_generic_meta():
    class Class(with_metaclass(GenericMeta, object)):
        pass

    # Bracket syntax should not work if class doesn't inherit from Generic.
    with pytest.raises(TypeError):
        _BadClass = Class[None]  # type: ignore
        assert not _BadClass

    # Should error if didn't specify type variables to Generic.
    with pytest.raises(TypeError):

        class _BadClass(Class, Generic[3]):  # type: ignore
            pass

        assert not _BadClass

    with pytest.raises(TypeError):

        class _BadClass(Class, Generic[int]):  # type: ignore
            pass

        assert not _BadClass

    # Declare a proper Generic class and check inheritance, equality, and instantiation.
    class _Class(Class, Generic[T]):
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


def test_weakref_slots():
    class Class(with_metaclass(GenericMeta, Generic[T])):
        __slots__ = ("__weakref__",)

    class SubClass(Class[T]):
        __slots__ = ()

    assert SubClass


if __name__ == "__main__":
    pytest.main()
