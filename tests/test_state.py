import sys
import pickle

import pytest  # noqa

from basicco.state import get_state, update_state, reducer


class _Class(object):
    __slots__ = ("a", "b", "c", "d")

    if sys.version_info[0:2] < (3, 4):
        __reduce__ = reducer


def test_get_state():
    class Class(object):
        def __init__(self):
            self.a = 1
            self.b = 2

    class SubClass(Class):
        def __init__(self):
            super(SubClass, self).__init__()
            self.c = 3

    assert get_state(SubClass()) == {"a": 1, "b": 2, "c": 3}


def test_get_slotted_state():
    class Class(object):
        __slots__ = ("a", "b")

        def __init__(self):
            self.a = 1
            self.b = 2

    class SubClass(Class):
        __slots__ = ("c",)

        def __init__(self):
            super(SubClass, self).__init__()
            self.c = 3

    assert get_state(SubClass()) == {"a": 1, "b": 2, "c": 3}


def test_get_class_state():
    class Class(object):
        a = 1
        b = 2

    assert get_state(Class) == dict(Class.__dict__)


def test_update_state():
    class Class(object):
        pass

    obj = Class()
    obj.d = 4
    update_state(obj, {"a": 1, "b": 2, "c": 3})

    assert obj.__dict__ == {"a": 1, "b": 2, "c": 3, "d": 4}


def test_update_slotted_state():
    class Class(object):
        __slots__ = ("a", "b", "c", "d")

    obj = Class()
    obj.d = 4
    update_state(obj, {"a": 1, "b": 2, "c": 3})

    assert obj.a == 1
    assert obj.b == 2
    assert obj.c == 3
    assert obj.d == 4


def test_reducer():
    obj = _Class()
    obj.a = 1
    obj.b = 2
    obj.c = 3
    obj.d = 4

    pickled_obj = pickle.loads(pickle.dumps(obj))

    assert pickled_obj.a == 1
    assert pickled_obj.b == 2
    assert pickled_obj.c == 3
    assert pickled_obj.d == 4


if __name__ == "__main__":
    pytest.main()