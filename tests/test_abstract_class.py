import pytest
import six

from basicco.abstract_class import Abstract, AbstractMeta, abstract, is_abstract


def test_class():
    assert isinstance(Abstract, AbstractMeta)


def test_abstract_class():
    @abstract
    class Class(six.with_metaclass(AbstractMeta, object)):
        pass

    with pytest.raises(TypeError):
        Class()

    class SubClass(Class):
        pass

    assert SubClass()


def test_super_new():
    class Class(six.with_metaclass(AbstractMeta, object)):
        @staticmethod
        def __new__(cls):
            self = super(Class, cls).__new__(cls)
            self.new_called = True
            return self

    obj = Class()
    assert obj.new_called is True

    class SubClass(Class):
        pass

    obj = SubClass()
    assert obj.new_called is True


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

        class Class(six.with_metaclass(AbstractMeta, object)):
            @decorator
            @abstract
            def method(self):
                pass

        assert is_abstract(Class.__dict__["method"])

        abstract_methods = getattr(Class, "__abstractmethods__")
        assert "method" in abstract_methods

        Class.new_method = decorator(abstract(lambda _: None))
        abstract_methods = getattr(Class, "__abstractmethods__")
        assert "new_method" in abstract_methods

        del Class.new_method
        abstract_methods = getattr(Class, "__abstractmethods__")
        assert "new_method" not in abstract_methods

        with pytest.raises(TypeError):
            Class()


def test_descriptor():
    class Descriptor(object):
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, owner):
            return 3

    class Class(six.with_metaclass(AbstractMeta, object)):
        @abstract
        @Descriptor
        def method(self):
            pass

    # Decorated descriptor object should be recognized as abstract.
    assert "method" in getattr(Class, "__abstractmethods__")


if __name__ == "__main__":
    pytest.main()
