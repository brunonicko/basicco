import pytest

from six import with_metaclass, PY2

from basicco.qualified import get_qualified_name, QualifiedMeta, _PARENT_ATTRIBUTE


@pytest.fixture()
def meta(pytestconfig):
    metacls = pytestconfig.getoption("metacls")
    if metacls:
        meta_module, meta_name = metacls.split("|")
        return getattr(__import__(meta_module, fromlist=[meta_name]), meta_name)
    else:
        return QualifiedMeta


@pytest.mark.parametrize("force_ast", (True, False))
def test_qualified_meta(meta, force_ast):

    # Asset reference to parent class.
    if PY2:
        assert getattr(ZM.BM, _PARENT_ATTRIBUTE) is ZM
        assert getattr(ZM.BM.CM, _PARENT_ATTRIBUTE) is ZM.BM
        assert getattr(AM.BM, _PARENT_ATTRIBUTE) is AM
        assert getattr(AM.BM.CM, _PARENT_ATTRIBUTE) is AM.BM

    # Get qualified name from class using the class attribute.
    assert AM.__qualname__ == "AM"
    assert AM.BM.__qualname__ == "AM.BM"
    assert AM.BM.CM.__qualname__ == "AM.BM.CM"

    # Get qualified name from class using the function.
    assert get_qualified_name(AM, force_ast=force_ast) == "AM"
    assert get_qualified_name(AM.BM, force_ast=force_ast) == "AM.BM"
    assert get_qualified_name(AM.BM.CM, force_ast=force_ast) == "AM.BM.CM"
    assert get_qualified_name(AM.BM.CM.dm, force_ast=force_ast) == "AM.BM.CM.dm"

    # Shouldn't be allowed to delete the attribute.
    with pytest.raises(TypeError):
        del AM.__qualname__


def test_qualname_property(meta):
    def func():
        class X(with_metaclass(meta, object)):
            class Y(with_metaclass(meta, object)):
                __qualname__ = "AA"

                class Z(with_metaclass(meta, object)):
                    pass

        return X

    if not PY2:
        assert (
            func().Y.Z.__qualname__
            == "test_qualname_property.<locals>.func.<locals>.X.Y.Z"
        )


class ZM(with_metaclass(QualifiedMeta, object)):
    class BM(with_metaclass(QualifiedMeta, object)):
        class CM(with_metaclass(QualifiedMeta, object)):
            def dm(self):
                pass


class AM(with_metaclass(QualifiedMeta, object)):
    class BM(with_metaclass(QualifiedMeta, object)):
        class CM(with_metaclass(QualifiedMeta, object)):
            def dm(self):
                pass


if __name__ == "__main__":
    pytest.main()
