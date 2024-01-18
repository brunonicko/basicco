# type: ignore

import random

import pytest

from basicco.func_tools import cache


def test_cache():
    data = {"count": 0}

    @cache
    def func():
        data["count"] += 1
        return random.random()

    results = set(func() for i in range(100))
    assert len(results) == 1
    assert data["count"] == 1


if __name__ == "__main__":
    pytest.main()
