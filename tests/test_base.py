import pytest
import pickle

from slotted import SlottedABC

from basicco import Base


def test_base():
    assert issubclass(Base, SlottedABC)

    obj = AM.BM.CM()
    pickled_obj = pickle.loads(pickle.dumps(obj))
    assert pickled_obj.a == 1
    assert pickled_obj.b == 2
    assert pickled_obj.c == 3


class AM(Base):
    class BM(Base):
        class CM(Base):
            __slots__ = ("a", "b", "__c")

            def __init__(self):
                self.a, self.b, self.__c = 1, 2, 3

            @property
            def c(self):
                return self.__c


if __name__ == "__main__":
    pytest.main()
