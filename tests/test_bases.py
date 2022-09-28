import pytest  # noqa

import basicco


def test_bases():
    assert basicco.CompatBaseMeta
    assert basicco.CompatBase
    assert basicco.CompatBase()

    assert basicco.BaseMeta
    assert basicco.Base
    assert basicco.Base()
    assert "__weakref__" in basicco.Base.__slots__


if __name__ == "__main__":
    pytest.main()
