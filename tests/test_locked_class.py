import pytest  # noqa
import six

from basicco.locked_class import (
    LockedClass,
    LockedClassMeta,
    is_locked,
    set_locked,
    unlocked_context,
)


def test_class():
    assert isinstance(LockedClass, LockedClassMeta)


def test_metaclass():
    class MyMeta(LockedClassMeta):
        @staticmethod
        def __new__(mcs, name, bases, dct, **kwargs):
            cls = super(MyMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)

            assert not is_locked(cls)
            cls.bar = "foo"

            return cls

        def __init__(cls, name, bases, dct, **kwargs):
            assert not is_locked(cls)
            cls.foobar = "foobar"

            super(MyMeta, cls).__init__(name, bases, dct, **kwargs)

            assert is_locked(cls)
            with pytest.raises(AttributeError):
                cls.foo = "bar"

    class Class(six.with_metaclass(MyMeta, object)):
        pass

    assert is_locked(Class)

    with pytest.raises(AttributeError):
        Class.foo = "bar"

    Class._foo = "bar"
    Class._Class__foo = "bar"
    Class.__foo__ = "bar"


def test_set_locked():
    class Class(six.with_metaclass(LockedClassMeta, object)):
        pass

    with pytest.raises(AttributeError):
        Class.foo = "bar"

    set_locked(Class, False)
    Class.foo = "bar"

    set_locked(Class, True)
    with pytest.raises(AttributeError):
        Class.foo = "bar"


def test_unlocked_context():
    class Class(six.with_metaclass(LockedClassMeta, object)):
        pass

    with pytest.raises(AttributeError):
        Class.foo = "bar"

    with unlocked_context(Class):
        Class.foo = "bar"

    with pytest.raises(AttributeError):
        Class.foo = "bar"


if __name__ == "__main__":
    pytest.main()
