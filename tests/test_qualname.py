import pytest

from basicco.qualname import qualname


@pytest.mark.parametrize("force_ast", (True, False))
def test_qualname(force_ast):
    assert qualname(A, force_ast=force_ast) == "A"
    assert qualname(A.B, force_ast=force_ast) == "A.B"
    assert qualname(A.B.C, force_ast=force_ast) == "A.B.C"
    assert qualname(A.B.C.d, force_ast=force_ast) == "A.B.C.d"


class A(object):
    class B(object):
        class C(object):
            def d(self):
                pass


if __name__ == "__main__":
    pytest.main()
