import pytest

from six import with_metaclass, PY2

from basicco.qualname import qualname, QualnameMeta, QualnameError, _PARENT_ATTRIBUTE


@pytest.mark.parametrize("force_ast", (True, False))
def test_qualname(force_ast):

    # Get qualified name for regular classes.
    assert qualname(A, force_ast=force_ast) == "A"
    assert qualname(A.B, force_ast=force_ast) == "A.B"
    assert qualname(A.B.C, force_ast=force_ast) == "A.B.C"
    assert qualname(A.B.C.d, force_ast=force_ast) == "A.B.C.d"

    # AST parsing should fail for classes generated on the fly.
    with pytest.raises(QualnameError):
        print(qualname(type("Z", (object,), {"BLA": 1}), force_ast=True))

    # Built-ins.
    assert qualname(int, force_ast=force_ast) == "int"
    assert qualname(float, force_ast=force_ast) == "float"
    assert qualname(bool, force_ast=force_ast) == "bool"


@pytest.mark.parametrize("force_ast", (True, False))
def test_qualname_meta(force_ast):

    # Asset reference to parent class.
    if PY2:
        assert getattr(ZM.BM, _PARENT_ATTRIBUTE) is ZM
        assert getattr(ZM.BM.CM, _PARENT_ATTRIBUTE) is ZM.BM
        assert getattr(AM.BM, _PARENT_ATTRIBUTE) is AM
        assert getattr(AM.BM.CM, _PARENT_ATTRIBUTE) is AM.BM

    # Get qualified name from class with QualnameMeta using the class attribute.
    assert AM.__qualname__ == "AM"
    assert AM.BM.__qualname__ == "AM.BM"
    assert AM.BM.CM.__qualname__ == "AM.BM.CM"

    # Get qualified name from class with QualnameMeta using the function.
    assert qualname(AM, force_ast=force_ast) == "AM"
    assert qualname(AM.BM, force_ast=force_ast) == "AM.BM"
    assert qualname(AM.BM.CM, force_ast=force_ast) == "AM.BM.CM"
    assert qualname(AM.BM.CM.dm, force_ast=force_ast) == "AM.BM.CM.dm"

    # Shouldn't be allowed to delete the attribute.
    with pytest.raises(TypeError):
        del AM.__qualname__


def test_qualname_property():
    def func():
        class X(with_metaclass(QualnameMeta, object)):
            class Y(with_metaclass(QualnameMeta, object)):
                __qualname__ = "AA"

                class Z(with_metaclass(QualnameMeta, object)):
                    pass

        return X

    if not PY2:
        assert func().Y.Z.__qualname__ == "test_qualname_property.<locals>.func.<locals>.X.Y.Z"


class A(object):
    class B(object):
        class C(object):
            def d(self):
                pass


class ZM(with_metaclass(QualnameMeta, object)):
    class BM(with_metaclass(QualnameMeta, object)):
        class CM(with_metaclass(QualnameMeta, object)):
            def dm(self):
                pass


class AM(with_metaclass(QualnameMeta, object)):
    class BM(with_metaclass(QualnameMeta, object)):
        class CM(with_metaclass(QualnameMeta, object)):
            def dm(self):
                pass


if __name__ == "__main__":
    pytest.main()
