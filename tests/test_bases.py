import pytest  # noqa

import basicco


def test_bases():
    assert basicco.CompatBaseMeta
    assert basicco.CompatBase
    assert basicco.CompatBase()

    assert basicco.BaseMeta
    assert basicco.Base
    assert basicco.Base()


if __name__ == "__main__":
    pytest.main()
