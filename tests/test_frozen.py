import pytest

from six import with_metaclass

from basicco.frozen import FROZEN_SLOT, frozen, FrozenMeta


def test_frozen_cls():

    @frozen(classes=True, instances=False)
    class Frozen(with_metaclass(FrozenMeta, object)):
        pass

    with pytest.raises(AttributeError):
        Frozen.attr = 1


def test_frozen_obj():

    @frozen(classes=False, instances=True)
    class Frozen(with_metaclass(FrozenMeta, object)):

        def __init__(self):
            self.attr = 0

    obj = Frozen()
    assert obj.attr == 0

    with pytest.raises(AttributeError):
        obj.attr = 1


def test_frozen_slotted_obj():

    @frozen(classes=False, instances=True)
    class Frozen(with_metaclass(FrozenMeta, object)):
        __slots__ = (FROZEN_SLOT, "attr")

        def __init__(self):
            self.attr = 0

    obj = Frozen()
    assert obj.attr == 0

    with pytest.raises(AttributeError):
        obj.attr = 1


if __name__ == "__main__":
    pytest.main()
