import pytest

from six import with_metaclass

from basicco.frozen import FROZEN_SLOT, frozen, FrozenMeta


@pytest.fixture()
def meta(pytestconfig):
    metacls = pytestconfig.getoption("metacls")
    if metacls:
        meta_module, meta_name = metacls.split("|")
        return getattr(__import__(meta_module, fromlist=[meta_name]), meta_name)
    else:
        return FrozenMeta


def test_frozen_classes(meta):

    # Freeze classes only.
    @frozen(classes=True, instances=False)
    class Frozen(with_metaclass(meta, object)):
        pass

    # A frozen class should not allow changes to class attributes.
    with pytest.raises(AttributeError):
        Frozen.attr = 1

    # Make sure the class actually gets frozen after the super init method runs.
    class SubFrozenMeta(meta):
        def __init__(cls, name, bases, dct, **kwargs):
            cls.attr = 1  # should not be frozen here

            super(SubFrozenMeta, cls).__init__(name, bases, dct, **kwargs)

            with pytest.raises(AttributeError):
                cls.attr = 2  # should be frozen here

    class SubFrozen(with_metaclass(SubFrozenMeta, Frozen)):
        pass

    with pytest.raises(AttributeError):
        SubFrozen.attr = 3

    # Should not be able to "unfreeze" the class.
    with pytest.raises(TypeError):

        @frozen(classes=False)
        class SubSubFrozen(SubFrozen):
            pass

        assert not SubSubFrozen

    # Should be able to freeze an already frozen class again.
    @frozen(classes=True)
    class SubSubFrozen(SubFrozen):
        pass

    assert SubSubFrozen


def test_frozen_instances(meta):

    # Freeze instances only.
    @frozen(classes=False, instances=True)
    class Frozen(with_metaclass(meta, object)):
        def __init__(self):
            self.attr = 0  # should not be frozen here

    obj = Frozen()
    assert obj.attr == 0

    with pytest.raises(AttributeError):
        obj.attr = 1  # should be frozen here

    # Should not be able to "unfreeze" instances.
    with pytest.raises(TypeError):

        @frozen(instances=False)
        class SubFrozen(Frozen):
            pass

        assert not SubFrozen

    # Should be able to freeze already frozen instances again.
    @frozen(instances=True)
    class SubFrozen(Frozen):
        pass

    assert SubFrozen

    # Should preserve custom __setattr__ and __delattr__ methods.
    @frozen(instances=True)
    class CustomFrozen(with_metaclass(meta, object)):
        def __init__(self):
            self.attr_a = 0  # should trigger custom __setattr__
            self.attr_b = 0
            del self.attr_b  # should trigger custom __delattr__

        def __setattr__(self, name, value):
            if name == "attr_a":
                value = 100
            super(CustomFrozen, self).__setattr__(name, value)

        def __delattr__(self, name):
            if name == "attr_b":
                value = -100
                super(CustomFrozen, self).__setattr__(name, value)
            else:
                super(CustomFrozen, self).__delattr__(name)

    assert CustomFrozen().attr_a == 100
    assert CustomFrozen().attr_b == -100


def test_frozen_slotted_instances(meta):

    # Error out if the slot is not available.
    @frozen(classes=False, instances=True)
    class Frozen(with_metaclass(meta, object)):
        __slots__ = ()

    with pytest.raises(AttributeError):
        Frozen()

    # Freeze instances only.
    @frozen(classes=False, instances=True)
    class Frozen(with_metaclass(meta, object)):
        __slots__ = (FROZEN_SLOT, "attr")  # need the slot

        def __init__(self):
            self.attr = 0  # should not be frozen here

    obj = Frozen()
    assert obj.attr == 0

    with pytest.raises(AttributeError):
        obj.attr = 1  # should be frozen here


def test_super_methods(meta):
    @frozen(instances=True)
    class Class(with_metaclass(meta, object)):
        def __setattr__(self, name, value):
            object.__setattr__(self, "setattr_called", True)
            super(Class, self).__setattr__(name, value)

        def __delattr__(self, name):
            object.__setattr__(self, "delattr_called", True)
            super(Class, self).__delattr__(name)

    obj = Class()
    object.__setattr__(obj, FROZEN_SLOT, False)
    obj.a = 1
    del obj.a
    assert getattr(obj, "setattr_called") is True
    assert getattr(obj, "setattr_called") is True


if __name__ == "__main__":
    pytest.main()
