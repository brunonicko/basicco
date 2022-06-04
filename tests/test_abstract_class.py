import pytest

from basicco.abstract_class import abstract_class


def test_abstract_class():
    @abstract_class
    class AbstractClass:
        @staticmethod
        def __new__(cls):
            self = super().__new__(cls)
            self.new_called = True
            return self

    with pytest.raises(NotImplementedError):
        AbstractClass()

    class Class(AbstractClass):
        pass

    obj = Class()
    assert obj.new_called is True

    class SubClass(Class):
        pass

    obj = SubClass()
    assert obj.new_called is True


if __name__ == "__main__":
    pytest.main()
