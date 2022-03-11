import pytest

from six import with_metaclass

from basicco import BaseMeta
from basicco.finalized import final, FinalizedMeta


@pytest.mark.parametrize("meta", (FinalizedMeta, BaseMeta))
def test_final_class(meta):
    @final
    class Class(with_metaclass(meta, object)):
        pass

    # Class should be tagged as final.
    assert getattr(Class, "__isfinalclass__") is True

    # Should error when trying to subclass from final class.
    with pytest.raises(TypeError):

        class SubClass(Class):  # type: ignore
            pass

        assert not SubClass


@pytest.mark.parametrize("meta", (FinalizedMeta, BaseMeta))
def test_final_method(meta):
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

        class Class(with_metaclass(meta, object)):
            @decorator
            @final
            def method(self):
                pass

        assert "method" in getattr(Class, "__finalmethods__")

        Class.new_method = decorator(final(lambda _: None))
        assert "new_method" in getattr(Class, "__finalmethods__")

        del Class.new_method
        assert "new_method" not in getattr(Class, "__finalmethods__")

        with pytest.raises(TypeError):

            class SubClass(Class):
                @decorator
                def method(self):  # type: ignore
                    pass

            assert not SubClass


@pytest.mark.parametrize("meta", (FinalizedMeta, BaseMeta))
def test_descriptor(meta):
    class Descriptor(object):
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, owner):
            return 3

    class Class(with_metaclass(meta, object)):
        @final
        @Descriptor
        def method(self):
            pass

    # Decorated descriptor object should be recognized as final.
    assert "method" in getattr(Class, "__finalmethods__")


if __name__ == "__main__":
    pytest.main()
