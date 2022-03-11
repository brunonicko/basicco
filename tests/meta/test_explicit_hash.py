import pytest

from six import with_metaclass

from basicco import BaseMeta
from basicco.explicit_hash import ExplicitHashMeta


@pytest.mark.parametrize("meta", (ExplicitHashMeta, BaseMeta))
def test_force_explicit_hash_declaration(meta):
    class Class(with_metaclass(meta, object)):
        pass

    with pytest.raises(TypeError):

        class SubClass(Class):
            def __eq__(self, other):
                raise NotImplementedError()

        assert not SubClass

    class SubClass(Class):
        def __hash__(self):
            raise NotImplementedError()

        def __eq__(self, other):
            raise NotImplementedError()

    assert SubClass


if __name__ == "__main__":
    pytest.main()
