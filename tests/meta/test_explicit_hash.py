import pytest

from six import with_metaclass

from basicco.explicit_hash import ExplicitHashMeta


@pytest.fixture()
def meta(pytestconfig):
    metacls = pytestconfig.getoption("metacls")
    if metacls:
        meta_module, meta_name = metacls.split("|")
        return getattr(__import__(meta_module, fromlist=[meta_name]), meta_name)
    else:
        return ExplicitHashMeta


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
