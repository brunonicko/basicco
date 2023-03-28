# type: ignore

import pytest

from basicco.sentinel import SentinelMeta, SentinelType


def test_sentinel():
    class MissingType(SentinelType):
        pass

    assert isinstance(MissingType, SentinelMeta)

    with pytest.raises(NotImplementedError):
        SentinelType()

    MISSING = MissingType()  # noqa

    assert MissingType() is MISSING

    with pytest.raises(TypeError):

        class _MissingType(MissingType):
            pass

        assert not _MissingType


if __name__ == "__main__":
    pytest.main()
