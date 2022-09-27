import pytest  # noqa

from basicco.safe_repr import safe_repr


def test_safe_repr():
    class Class(object):
        @safe_repr
        def __repr__(self):
            raise RuntimeError("oh oh")

    obj = Class()
    standard_repr = object.__repr__(obj)
    assert repr(obj) == standard_repr[:-1] + "; repr failed due to 'RuntimeError: oh oh'>"


if __name__ == "__main__":
    pytest.main()
