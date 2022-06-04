import pytest

from basicco.explicit_hash import ExplicitHashMeta


def test_force_explicit_hash_declaration():
    class Class(metaclass=ExplicitHashMeta):
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
