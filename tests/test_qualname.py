from __future__ import absolute_import, division, print_function

import pytest  # noqa

from basicco.qualname import qualname, QualnameError


@pytest.mark.parametrize("force_ast", (True, False))
def test_qualname(force_ast):

    # Get qualified name for regular classes.
    assert qualname(X, force_ast=force_ast) == "X"
    assert qualname(X.Y, force_ast=force_ast) == "X.Y"
    assert qualname(X.Y.Z, force_ast=force_ast) == "X.Y.Z"
    assert qualname(X.Y.Z.method, force_ast=force_ast) == "X.Y.Z.method"

    assert qualname(A, force_ast=force_ast) == "A"
    assert qualname(A.Y, force_ast=force_ast) == "A.Y"
    assert qualname(A.Y.C, force_ast=force_ast) == "A.Y.C"
    assert qualname(A.Y.C.method, force_ast=force_ast) == "A.Y.C.method"

    # AST parsing should fail for classes generated on the fly.
    with pytest.raises(QualnameError):
        print(qualname(type("Z", (object,), {"BLA": 1}), force_ast=True))

    # Built-ins.
    assert qualname(int, force_ast=force_ast) == "int"
    assert qualname(float, force_ast=force_ast) == "float"
    assert qualname(bool, force_ast=force_ast) == "bool"


class X(object):
    class Y(object):
        class Z(object):
            def method(self):
                pass


class A(object):
    class Y(object):
        class C(object):
            def method(self):
                pass


if __name__ == "__main__":
    pytest.main()
