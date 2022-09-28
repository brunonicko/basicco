import copy
import pickle

import pytest  # noqa

from basicco.hash_cache_wrapper import HashCacheWrapper


def test_pickling():
    cache = HashCacheWrapper(12345)
    assert cache == 12345

    assert pickle.loads(pickle.dumps(cache)) is None


def test_copy():
    cache = HashCacheWrapper(12345)
    assert cache == 12345

    assert copy.copy(cache) is None


def test_deepcopy():
    cache = HashCacheWrapper(12345)
    assert cache == 12345

    assert copy.deepcopy(cache) is None


if __name__ == "__main__":
    pytest.main()
