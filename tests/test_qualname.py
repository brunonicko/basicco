import pytest

from six import with_metaclass

from basicco.qualname import qualname, QualnameMeta, QualnameError


@pytest.mark.parametrize("force_ast", (True, False))
def test_qualname(force_ast):

    # Get qualified name for regular classes.
    assert qualname(A, force_ast=force_ast) == "A"
    assert qualname(A.B, force_ast=force_ast) == "A.B"
    assert qualname(A.B.C, force_ast=force_ast) == "A.B.C"
    assert qualname(A.B.C.d, force_ast=force_ast) == "A.B.C.d"

    # AST parsing should fail for classes generated on the fly.
    with pytest.raises(QualnameError):
        qualname(type("Z", (object,), {}), force_ast=True)

    # Built-ins.
    assert qualname(int, force_ast=force_ast) == "int"
    assert qualname(float, force_ast=force_ast) == "float"
    assert qualname(bool, force_ast=force_ast) == "bool"


@pytest.mark.parametrize("force_ast", (True, False))
def test_qualname_meta(force_ast):

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

    # Class repr should have the qualified name in it.
    assert AM.__qualname__ in repr(AM)
    assert AM.BM.__qualname__ in repr(AM.BM)
    assert AM.BM.CM.__qualname__ in repr(AM.BM.CM)


class A(object):
    class B(object):
        class C(object):
            def d(self):
                pass


class AM(with_metaclass(QualnameMeta, object)):
    class BM(with_metaclass(QualnameMeta, object)):
        class CM(with_metaclass(QualnameMeta, object)):
            def dm(self):
                pass


if __name__ == "__main__":
    pytest.main()
