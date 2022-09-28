import pytest  # noqa
import six

from basicco.default_dir import DefaultDir, DefaultDirMeta


def test_class():
    assert isinstance(DefaultDir, DefaultDirMeta)


def test_metaclass():
    class Class(six.with_metaclass(DefaultDirMeta, object)):
        c = None
        d = None

        @property
        def prop_a(self):
            return None

    class SubClass(Class):
        __slots__ = ("a", "b")

        def __dir__(self):
            return super(SubClass, self).__dir__()

        @property
        def prop_b(self):
            return None

    obj = SubClass()
    assert set(dir(obj)).issuperset(
        {
            "__class__",
            "__delattr__",
            "__dict__",
            "__dir__",
            "__doc__",
            "__format__",
            "__getattribute__",
            "__hash__",
            "__init__",
            "__module__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "__weakref__",
            "a",
            "b",
            "c",
            "d",
            "prop_a",
            "prop_b",
        }
    )


if __name__ == "__main__":
    pytest.main()
