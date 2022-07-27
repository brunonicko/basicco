from __future__ import absolute_import, division, print_function

import pytest  # noqa

from basicco.fabricate_value import fabricate_value


def test_fabricate_value():
    assert fabricate_value(None, 3) == 3
    assert fabricate_value(str, 3) == "3"
    assert fabricate_value("str", 3) == "3"


if __name__ == "__main__":
    pytest.main()
