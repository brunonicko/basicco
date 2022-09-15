import pytest  # noqa

from basicco import caller_module


def test_caller_module():
    def func():
        return caller_module.caller_module()

    assert func() == __name__


if __name__ == "__main__":
    pytest.main()
