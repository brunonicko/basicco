import pytest

from tippo import TypeVar, Generic

from basicco.get_mro import get_mro


T = TypeVar("T")


def test_generic_mro():
    T = TypeVar("T")  # type: ignore  # noqa

    class Base(Generic[T]):
        pass

    class SubBase(Base[T]):
        pass

    class SubSubBase(SubBase[T], Base[T]):
        pass

    assert get_mro(SubSubBase) == (SubSubBase, SubBase, Base, Generic, object)


if __name__ == "__main__":
    pytest.main()
