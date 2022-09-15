import pytest  # noqa

from basicco.unique_iterator import unique_iterator


def test_unique_iterator():
    assert list(unique_iterator([1, 2, 3, 3, 4, 4, 5])) == [1, 2, 3, 4, 5]


if __name__ == "__main__":
    pytest.main()
