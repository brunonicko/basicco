from __future__ import absolute_import, division, print_function

import pytest

from basicco.context_vars import ContextVar


_var = ContextVar("_var")  # type: ContextVar[str]
_default_var = ContextVar("_default_var", default="default")  # type: ContextVar[str]


def test_var():
    with pytest.raises(LookupError):
        _var.get()
    assert _var.get(None) is None

    token = _var.set("foo")
    assert _var.get() == "foo"
    _var.reset(token)

    with pytest.raises(LookupError):
        _var.get()
    assert _var.get(None) is None


def test_default_var():
    assert _default_var.get() == "default"
    assert _var.get(None) is None

    token = _default_var.set("foo")
    assert _default_var.get() == "foo"
    _default_var.reset(token)

    assert _default_var.get() == "default"
    assert _var.get(None) is None


if __name__ == "__main__":
    pytest.main()
