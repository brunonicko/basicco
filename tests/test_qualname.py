import pytest

from six import with_metaclass

from basicco.qualname import qualname, QualnameMeta, QualnameError


@pytest.mark.parametrize("force_ast", (True, False))
def test_qualname(force_ast):
    assert qualname(A, force_ast=force_ast) == "A"
    assert qualname(A.B, force_ast=force_ast) == "A.B"
    assert qualname(A.B.C, force_ast=force_ast) == "A.B.C"
    assert qualname(A.B.C.d, force_ast=force_ast) == "A.B.C.d"

    with pytest.raises(QualnameError):
        qualname(type("Z", (object,), {}), force_ast=True)


@pytest.mark.parametrize("force_ast", (True, False))
def test_qualname_meta(force_ast):
    assert AM.__qualname__ == "AM"
    assert AM.BM.__qualname__ == "AM.BM"
    assert AM.BM.CM.__qualname__ == "AM.BM.CM"

    assert qualname(AM, force_ast=force_ast) == "AM"
    assert qualname(AM.BM, force_ast=force_ast) == "AM.BM"
    assert qualname(AM.BM.CM, force_ast=force_ast) == "AM.BM.CM"
    assert qualname(AM.BM.CM.dm, force_ast=force_ast) == "AM.BM.CM.dm"

    with pytest.raises(TypeError):
        del AM.__qualname__

    assert repr(AM) == "<class '{}.{}'>".format(__name__, AM.__qualname__)
    assert repr(AM.BM) == "<class '{}.{}'>".format(__name__, AM.BM.__qualname__)
    assert repr(AM.BM.CM) == "<class '{}.{}'>".format(__name__, AM.BM.CM.__qualname__)


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
