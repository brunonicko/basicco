import pytest  # noqa
from tippo import GenericMeta

import basicco


def test_bases():
    assert basicco.CompatBaseMeta
    assert basicco.CompatBase
    assert basicco.CompatBase()

    assert issubclass(basicco.CompatBaseMeta, GenericMeta)

    assert basicco.BaseMeta
    assert basicco.Base
    assert basicco.Base()
    assert "__weakref__" in basicco.Base.__slots__


if __name__ == "__main__":
    pytest.main()
