import pytest

from six import with_metaclass

from basicco.final import final, FinalMeta


def test_final_class():
    @final
    class Class(with_metaclass(FinalMeta, object)):
        pass

    assert getattr(Class, "__isfinalclass__") is True

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

    for decorator in decorators:

        class Class(with_metaclass(FinalMeta, object)):
            @decorator
            @final
            def method(self):
                pass

        assert "method" in getattr(Class, "__finalmethods__")

        with pytest.raises(TypeError):

            class SubClass(Class):
                @decorator
                def method(self):  # type: ignore
                    pass

            assert not SubClass


if __name__ == "__main__":
    pytest.main()
