import collections

import pytest  # noqa
from tippo import NamedTuple

from basicco.named_tuple import defaults


def test_defaults():
    Point = collections.namedtuple("Point", ("x", "y"))
    defaults(x=0, y=0)(Point)
    assert Point() == (0, 0)  # noqa
    assert Point(1) == (1, 0)  # noqa
    assert Point(1, 2) == (1, 2)

    with pytest.raises(TypeError):
        defaults(x=0)(Point)(1)


def test_typed_defaults():
    Point = NamedTuple("Point", (("x", int), ("y", int)))  # noqa
    defaults(x=0, y=0)(Point)
    assert Point() == (0, 0)  # noqa
    assert Point(1) == (1, 0)  # noqa
    assert Point(1, 2) == (1, 2)  # noqa

    with pytest.raises(TypeError):
        defaults(x=0)(Point)(1)


if __name__ == "__main__":
    pytest.main()
