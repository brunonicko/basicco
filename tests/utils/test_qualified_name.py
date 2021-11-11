import pytest

from basicco.utils.qualified_name import get_qualified_name, QualnameError


@pytest.mark.parametrize("force_ast", (True, False))
def test_get_qualified_name(force_ast):

    # Get qualified name for regular classes.
    assert get_qualified_name(X, force_ast=force_ast) == "X"
    assert get_qualified_name(X.Y, force_ast=force_ast) == "X.Y"
    assert get_qualified_name(X.Y.Z, force_ast=force_ast) == "X.Y.Z"
    assert get_qualified_name(X.Y.Z.method, force_ast=force_ast) == "X.Y.Z.method"

    assert get_qualified_name(A, force_ast=force_ast) == "A"
    assert get_qualified_name(A.Y, force_ast=force_ast) == "A.Y"
    assert get_qualified_name(A.Y.C, force_ast=force_ast) == "A.Y.C"
    assert get_qualified_name(A.Y.C.method, force_ast=force_ast) == "A.Y.C.method"

    # AST parsing should fail for classes generated on the fly.
    with pytest.raises(QualnameError):
        print(get_qualified_name(type("Z", (object,), {"BLA": 1}), force_ast=True))

    # Built-ins.
    assert get_qualified_name(int, force_ast=force_ast) == "int"
    assert get_qualified_name(float, force_ast=force_ast) == "float"
    assert get_qualified_name(bool, force_ast=force_ast) == "bool"


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
