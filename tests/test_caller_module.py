# type: ignore

import pytest

from basicco import caller_module


def test_caller_module():
    def func():
        return caller_module.caller_module()

    assert func() == __name__


def test_auto_called_module():
    @caller_module.auto_caller_module("extra_paths", "cls_module")
    def func(extra_paths=(), cls_module=None, expects=((), None)):
        assert extra_paths == expects[0]
        assert cls_module == expects[1]

    func(expects=((__name__,), __name__))
    func(extra_paths=("foo", "bar"), expects=(("foo", "bar"), __name__))
    func(cls_module="foobar", expects=((__name__,), "foobar"))
    func(
        extra_paths=("foo", "bar"),
        cls_module="foobar",
        expects=(("foo", "bar"), "foobar"),
    )


if __name__ == "__main__":
    pytest.main()
