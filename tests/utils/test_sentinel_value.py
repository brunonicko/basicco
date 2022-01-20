import pytest
from pickle import loads, dumps

from basicco.utils.sentinel_value import sentinel_value


NothingType, Nothing = sentinel_value("Nothing")
EverythingType, Everything = sentinel_value("Everything", boolean=True)


def test_sentinel_value():
    assert type(Nothing) is NothingType
    assert type(Everything) is EverythingType

    assert Nothing is NothingType()
    assert Everything is EverythingType()

    assert Nothing is not Everything
    assert NothingType is not EverythingType

    assert isinstance(Nothing, NothingType)
    assert isinstance(Everything, EverythingType)


def test_boolean():
    assert bool(Nothing) is False
    assert bool(Everything) is True


def test_pickling():
    assert loads(dumps(Nothing)) is Nothing
    assert loads(dumps(NothingType)) is NothingType


if __name__ == "__main__":
    pytest.main()
