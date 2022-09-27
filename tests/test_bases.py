import pytest  # noqa

import basicco


def test_bases():
    assert basicco.BaseMeta
    assert basicco.Base
    assert basicco.Base()

    assert basicco.BetterBaseMeta
    assert basicco.BetterBase
    assert basicco.BetterBase()


if __name__ == "__main__":
    pytest.main()
