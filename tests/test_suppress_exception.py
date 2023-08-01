# type: ignore

import pytest

from basicco.suppress_exception import suppress_exception


def test_suppress_exception():
    with suppress_exception(TypeError):
        raise TypeError()

    with suppress_exception(ValueError):
        with suppress_exception(TypeError):
            raise ValueError()

    with pytest.raises(RuntimeError):
        with suppress_exception(ValueError):
            raise RuntimeError()


if __name__ == "__main__":
    pytest.main()
