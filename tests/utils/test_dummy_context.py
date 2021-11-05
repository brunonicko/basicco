import pytest

from basicco.utils.dummy_context import dummy_context


def test_dummy_context():
    with dummy_context():
        pass


if __name__ == "__main__":
    pytest.main()
