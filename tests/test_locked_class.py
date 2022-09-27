import pytest  # noqa
import six

from basicco.locked_class import LockedClassMeta, LockedClass


def test_class():
    assert isinstance(LockedClass, LockedClassMeta)


def test_metaclass():
    class MyMeta(LockedClassMeta):
        @staticmethod
        def __new__(mcs, name, bases, dct, **kwargs):
            cls = super(MyMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)

            assert not cls.__locked__
            cls.bar = "foo"

            return cls

        def __init__(cls, name, bases, dct, **kwargs):
            assert not cls.__locked__
            cls.foobar = "foobar"

            super(MyMeta, cls).__init__(name, bases, dct, **kwargs)

            assert cls.__locked__
            with pytest.raises(AttributeError):
                Class.foo = "bar"

    class Class(six.with_metaclass(LockedClassMeta, object)):
        pass

    assert Class.__locked__

    with pytest.raises(AttributeError):
        Class.foo = "bar"

    Class._foo = "bar"
    Class._Class__foo = "bar"
    Class.__foo__ = "bar"


if __name__ == "__main__":
    pytest.main()
