import pytest

from basicco.utils.caller_module import get_caller_module


def test_get_caller_module():
    def func():
        return get_caller_module()

    assert func() == __name__


if __name__ == "__main__":
    pytest.main()
