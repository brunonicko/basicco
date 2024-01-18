# type: ignore

import uuid

import pytest

from basicco.func_tools import cache, lru_cache


def test_cache():
    data = {"count": 0}

    @cache
    def func():
        data["count"] += 1
        return uuid.uuid4()

    results = set(func() for i in range(100))
    assert len(results) == 1
    assert data["count"] == 1


def test_lru_cache_a():
    data = {"count": 0}

    @lru_cache
    def func(a, b, c=None, d=None):  # noqa
        data["count"] += 1
        return uuid.uuid4()

    results = set()
    for i in range(100):
        for j in range(20):
            results.add(func(i, i + 1, c=i + 2, d=i + 3))

    assert len(results) == 100
    assert data["count"] == 100


def test_lru_cache_b():
    data = {"count": 0}

    @lru_cache()
    def func(a, b, c=None, d=None):  # noqa
        data["count"] += 1
        return uuid.uuid4()

    results = set()
    for i in range(100):
        for j in range(20):
            results.add(func(i, i + 1, c=i + 2, d=i + 3))

    assert len(results) == 100
    assert data["count"] == 100


if __name__ == "__main__":
    pytest.main()
