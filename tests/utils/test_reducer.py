import pytest
import pickle

from basicco.utils.reducer import reducer


def test_reducer():
    x = X("x")
    x_y = X.Y("x_y")
    x_y_z = X.Y.Z("x_y_z")

    a = A("a")
    a_y = A.Y("a_y")
    a_y_c = A.Y.C("a_y_c")

    assert pickle.loads(pickle.dumps(x)).n == x.n
    assert pickle.loads(pickle.dumps(x_y)).n == x_y.n
    assert pickle.loads(pickle.dumps(x_y_z)).n == x_y_z.n

    assert pickle.loads(pickle.dumps(a)).n == a.n
    assert pickle.loads(pickle.dumps(a_y)).n == a_y.n
    assert pickle.loads(pickle.dumps(a_y_c)).n == a_y_c.n

    # Should fail for classes generated on the fly.
    with pytest.raises(pickle.PickleError):
        print(pickle.loads(pickle.dumps(type("Z", (object,), {"BLA": 1})())))


class Pickable(object):
    __reduce__ = reducer

    def __init__(self, n):
        self.n = n


class X(Pickable):
    class Y(Pickable):
        class Z(Pickable):
            pass


class A(Pickable):
    class Y(Pickable):
        class C(Pickable):
            pass


if __name__ == "__main__":
    pytest.main()
