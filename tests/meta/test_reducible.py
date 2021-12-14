import pytest
import pickle

from six import with_metaclass

from basicco.reducible import ReducibleMeta


def test_pickle_base():
    obj = AM.BM()
    assert hasattr(obj, "__dict__")
    pickled_obj = pickle.loads(pickle.dumps(obj))
    assert pickled_obj.a == 1
    assert pickled_obj.b == 2
    assert pickled_obj.c == 3


def test_pickle_slotted_base():
    obj = AM.BM.CM()
    assert not hasattr(obj, "__dict__")
    pickled_obj = pickle.loads(pickle.dumps(obj))
    assert pickled_obj.a == 1
    assert pickled_obj.b == 2
    assert pickled_obj.c == 3


class Reducible(with_metaclass(ReducibleMeta, object)):
    __slots__ = ()


class AM(Reducible):
    class BM(Reducible):
        def __init__(self):
            self.a, self.b, self.__c = 1, 2, 3

        @property
        def c(self):
            return self.__c

        class CM(Reducible):
            __slots__ = ("a", "b", "__c")

            def __init__(self):
                self.a, self.b, self.__c = 1, 2, 3

            @property
            def c(self):
                return self.__c


if __name__ == "__main__":
    pytest.main()
