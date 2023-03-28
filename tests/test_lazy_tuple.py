# type: ignore

import pytest

from basicco.lazy_tuple import LazyTuple


def _generator(shared):
    for i in range(100):
        shared.append(i)
        yield i


def test_lazy_tuple():
    shared = []

    lt = LazyTuple(_generator(shared))
    assert shared == []

    assert lt[3] == 3
    assert shared == list(range(4))

    assert lt[6] == 6
    assert shared == list(range(7))

    assert len(lt) == 100
    assert shared == list(range(100))

    assert lt == tuple(range(100))
    assert hash(lt) == hash(tuple(range(100)))


if __name__ == "__main__":
    pytest.main()
