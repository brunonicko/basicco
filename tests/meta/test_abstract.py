import pytest

from six import with_metaclass

from basicco.abstract import abstract, AbstractMeta


@pytest.fixture()
def meta(pytestconfig):
    metacls = pytestconfig.getoption("metacls")
    if metacls:
        meta_module, meta_name = metacls.split("|")
        return getattr(__import__(meta_module, fromlist=[meta_name]), meta_name)
    else:
        return AbstractMeta


def test_abstract_class(meta):
    @abstract
    class Class(with_metaclass(meta, object)):
        pass

    with pytest.raises(TypeError):
        Class()

    class SubClass(Class):
        pass

    assert SubClass()


def test_super_new(meta):
    class Class(with_metaclass(meta, object)):
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


def test_abstract_method(meta):
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

        class Class(with_metaclass(meta, object)):
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


def test_descriptor(meta):
    class Descriptor(object):
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, owner):
            return 3

    class Class(with_metaclass(meta, object)):
        @abstract
        @Descriptor
        def method(self):
            pass

    # Decorated descriptor object should be recognized as abstract.
    assert "method" in getattr(Class, "__abstractmethods__")


if __name__ == "__main__":
    pytest.main()
