import pytest  # noqa
import six

from basicco.explicit_hash import ExplicitHash, ExplicitHashMeta


def test_class():
    assert isinstance(ExplicitHash, ExplicitHashMeta)


def test_force_explicit_hash_declaration():
    class Class(six.with_metaclass(ExplicitHashMeta, object)):
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
