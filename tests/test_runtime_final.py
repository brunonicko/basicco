import pytest  # noqa
import six
from tippo import Generic, GenericMeta, TypeVar

from basicco.runtime_final import _FINAL_CLASS_TAG  # noqa
from basicco.runtime_final import _FINAL_METHODS  # noqa
from basicco.runtime_final import RuntimeFinal, RuntimeFinalMeta, final


def test_class():
    assert isinstance(RuntimeFinal, RuntimeFinalMeta)


def test_final_class():
    @final
    class Class(six.with_metaclass(RuntimeFinalMeta, object)):
        pass

    # Class should be tagged as final.
    assert getattr(Class, _FINAL_CLASS_TAG) is True

    # Should error when trying to subclass from final class.
    with pytest.raises(TypeError):

        class SubClass(Class):  # type: ignore
            pass

        assert not SubClass


def test_final_method():
    def dummy_decorator(func):
        return func

    class PropertyLikeDescriptor(object):
        def __init__(self, fget):
            self.fget = fget

        def __get__(self, instance, owner):
            return 3

    decorators = [
        dummy_decorator,
        PropertyLikeDescriptor,
        classmethod,
        staticmethod,
        property,
    ]

    # Different kinds of decorated members should be recognized as final.
    for decorator in decorators:

        class Class(six.with_metaclass(RuntimeFinalMeta, object)):
            @decorator
            @final
            def method(self):
                pass

        assert "method" in getattr(Class, _FINAL_METHODS)

        Class.new_method = decorator(final(lambda _: None))
        assert "new_method" in getattr(Class, _FINAL_METHODS)

        del Class.new_method
        assert "new_method" not in getattr(Class, _FINAL_METHODS)

        with pytest.raises(TypeError):

            class SubClass(Class):
                @decorator
                def method(self):  # type: ignore
                    pass

            assert not SubClass


def test_descriptor():
    class Descriptor(object):
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, owner):
            return 3

    class Class(six.with_metaclass(RuntimeFinalMeta, object)):
        @final
        @Descriptor
        def method(self):
            pass

    # Decorated descriptor object should be recognized as final.
    assert "method" in getattr(Class, _FINAL_METHODS)


def test_generic():
    T = TypeVar("T")  # type: ignore  # noqa

    class BaseMeta(RuntimeFinalMeta, GenericMeta):
        pass

    class Base(six.with_metaclass(BaseMeta, Generic[T])):
        @final
        def method(self):
            pass

    assert Base[int]
    assert Base[T]

    assert repr(Base[int])
    assert repr(Base[T])

    class SubBase(Base[T]):
        pass

    assert SubBase


if __name__ == "__main__":
    pytest.main()
