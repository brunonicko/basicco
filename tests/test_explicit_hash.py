import pytest  # noqa
import six
import tippo

from basicco.explicit_hash import ExplicitHash, ExplicitHashMeta, set_to_none


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


def test_set_to_none():
    class Class(object):
        @set_to_none
        def __hash__(self):
            error = "not hashable"
            raise TypeError(error)

    assert not issubclass(Class, tippo.Hashable)
    assert not isinstance(Class(), tippo.Hashable)
    assert Class.__hash__ is None


if __name__ == "__main__":
    pytest.main()
