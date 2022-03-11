import pytest

from basicco import BaseMeta, Base


def test_base():
    assert isinstance(Base, BaseMeta)
    assert isinstance(Base(), Base)


if __name__ == "__main__":
    pytest.main()
