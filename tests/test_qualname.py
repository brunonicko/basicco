import pytest  # noqa
import six

from basicco.qualname import Qualnamed, QualnamedMeta, QualnameError, qualname


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


def test_class():
    assert isinstance(Qualnamed, QualnamedMeta)

    assert "{}.QA.QY.QC.QD".format(__name__) in repr(QA.QY.QC.QD())


def test_metaclass():
    assert QX.__qualname__ == "QX"
    assert QX.QY.__qualname__ == "QX.QY"
    assert QX.QY.QZ.__qualname__ == "QX.QY.QZ"

    assert QA.__qualname__ == "QA"
    assert QA.QY.__qualname__ == "QA.QY"
    assert QA.QY.QC.__qualname__ == "QA.QY.QC"

    assert repr(QX.QY.QZ) == "<class '{}.QX.QY.QZ'>".format(__name__)
    assert repr(QA.QY.QC) == "<class '{}.QA.QY.QC'>".format(__name__)

    QX.QY.QZ.__qualname__ = "QX.QY.QZ.CUSTOM"
    QX.QY.__qualname__ = "QX.QY.CUSTOM"
    QX.__qualname__ = "QX.CUSTOM"

    QA.QY.QC.__qualname__ = "QA.QY.QC.CUSTOM"
    QA.QY.__qualname__ = "QA.QY.CUSTOM"
    QA.__qualname__ = "QA.CUSTOM"

    assert QX.__qualname__ == "QX.CUSTOM"
    assert QX.QY.__qualname__ == "QX.QY.CUSTOM"
    assert QX.QY.QZ.__qualname__ == "QX.QY.QZ.CUSTOM"

    assert QA.__qualname__ == "QA.CUSTOM"
    assert QA.QY.__qualname__ == "QA.QY.CUSTOM"
    assert QA.QY.QC.__qualname__ == "QA.QY.QC.CUSTOM"

    QX.QY.QZ.__qualname__ = "QX.QY.QZ"
    QX.QY.__qualname__ = "QX.QY"
    QX.__qualname__ = "QX"

    QA.QY.QC.__qualname__ = "QA.QY.QC"
    QA.QY.__qualname__ = "QA.QY"
    QA.__qualname__ = "QA"

    assert QX.__qualname__ == "QX"
    assert QX.QY.__qualname__ == "QX.QY"
    assert QX.QY.QZ.__qualname__ == "QX.QY.QZ"

    assert QA.__qualname__ == "QA"
    assert QA.QY.__qualname__ == "QA.QY"
    assert QA.QY.QC.__qualname__ == "QA.QY.QC"


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


class QX(six.with_metaclass(QualnamedMeta, object)):
    class QY(six.with_metaclass(QualnamedMeta, object)):
        class QZ(six.with_metaclass(QualnamedMeta, object)):
            pass


class QA(six.with_metaclass(QualnamedMeta, object)):
    class QY(six.with_metaclass(QualnamedMeta, object)):
        class QC(six.with_metaclass(QualnamedMeta, object)):
            class QD(Qualnamed):
                pass


if __name__ == "__main__":
    pytest.main()
