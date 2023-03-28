# type: ignore

import pytest

from basicco.recursive_repr import recursive_repr


def test_recursive_repr():
    @recursive_repr
    def my_repr(_self, prefix="MyRepr<", suffix=">"):
        return prefix + my_repr(_self) + suffix

    assert my_repr(object()) == "MyRepr<...>"  # noqa


if __name__ == "__main__":
    pytest.main()
