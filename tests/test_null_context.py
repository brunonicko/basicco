# type: ignore

import pytest

from basicco.null_context import null_context


def test_null_context():
    with null_context() as result:
        assert result is None

    with null_context(42) as result:
        assert result == 42


if __name__ == "__main__":
    pytest.main()
