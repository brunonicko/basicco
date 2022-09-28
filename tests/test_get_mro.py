import pytest  # noqa
import six
from tippo import Generic, TypeVar

from basicco.get_mro import get_mro, preview_mro, resolve_origin


def test_resolve_origin():
    T = TypeVar("T")  # type: ignore  # noqa

    class Base(Generic[T]):
        pass

    assert resolve_origin(Base) is Base
    assert resolve_origin(Base[int]) is Base
    assert resolve_origin(Base[T]) is Base


def test_get_mro():
    T = TypeVar("T")  # type: ignore  # noqa

    class Base(Generic[T]):
        pass

    class SubBase(Base[T]):
        pass

    class SubSubBase(SubBase[T], Base[T]):
        pass

    assert get_mro(SubSubBase) == (SubSubBase, SubBase, Base, Generic, object)
    assert get_mro(SubSubBase[T]) == (SubSubBase, SubBase, Base, Generic, object)
    assert get_mro(SubSubBase[int]) == (SubSubBase, SubBase, Base, Generic, object)


def test_preview_mro():
    class M(type):
        pass

    class A(six.with_metaclass(M, object)):
        pass

    class B(A):
        pass

    class C(A):
        pass

    class D(B, C):
        pass

    assert preview_mro(B, C) == get_mro(D)[1:]


if __name__ == "__main__":
    pytest.main()
