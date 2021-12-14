import os
import pytest

from basicco import BaseMeta, Base


def test_base_meta_integration():
    base_dir = os.path.join(os.path.dirname(__file__), "meta")
    test_files = [
        os.path.join(base_dir, f)
        for f in os.listdir(base_dir)
        if f.startswith("test_") and f.endswith(".py")
    ]
    for test_file in sorted(test_files):
        pytest.main([test_file, "--metacls=basicco|BaseMeta", "-qq"])


def test_base():
    assert isinstance(Base, BaseMeta)
    assert isinstance(Base(), Base)


if __name__ == "__main__":
    pytest.main()
