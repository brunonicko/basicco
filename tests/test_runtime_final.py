from __future__ import absolute_import, division, print_function

import pytest
import six

from basicco.runtime_final import _FINAL_CLASS_TAG, _FINAL_METHODS, final, FinalizedMeta


def test_final_class():
    @final
    class Class(six.with_metaclass(FinalizedMeta, object)):
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

        class Class(six.with_metaclass(FinalizedMeta, object)):
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

    class Class(six.with_metaclass(FinalizedMeta, object)):
        @final
        @Descriptor
        def method(self):
            pass

    # Decorated descriptor object should be recognized as final.
    assert "method" in getattr(Class, _FINAL_METHODS)


if __name__ == "__main__":
    pytest.main()
