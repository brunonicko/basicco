import pytest

from six import with_metaclass

from basicco.abstract import abstract, AbstractMeta


def test_abstract_class():
    @abstract
    class Class(with_metaclass(AbstractMeta, object)):
        pass

    with pytest.raises(TypeError):
        Class()

    class SubClass(Class):
        pass

    assert SubClass()


def test_abstract_method():
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

    # Different kinds of decorated members should be recognized as abstract.
    for decorator in decorators:

        class Class(with_metaclass(AbstractMeta, object)):
            @decorator
            @abstract
            def method(self):
                pass

        assert "method" in getattr(Class, "__abstractmethods__")

        Class.new_method = decorator(abstract(lambda _: None))
        assert "new_method" in getattr(Class, "__abstractmethods__")

        del Class.new_method
        assert "new_method" not in getattr(Class, "__abstractmethods__")

        with pytest.raises(TypeError):
            Class()


def test_descriptor():
    class Descriptor(object):
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, owner):
            return 3

    class Class(with_metaclass(AbstractMeta, object)):
        @abstract
        @Descriptor
        def method(self):
            pass

    # Decorated descriptor object should be recognized as abstract.
    assert "method" in getattr(Class, "__abstractmethods__")


if __name__ == "__main__":
    pytest.main()
