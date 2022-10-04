import copy
import pickle
import sys

import pytest  # noqa
import six

from basicco.obj_state import Reducible, ReducibleMeta, get_state, reducer, update_state


class _Class(object):
    __slots__ = ("a", "b", "c", "d")

    if sys.version_info[0:2] < (3, 4):
        __reduce__ = reducer


class _ReducibleClass(six.with_metaclass(ReducibleMeta, object)):
    __slots__ = ("a", "b", "c", "d")


class _SlottedClass(six.with_metaclass(ReducibleMeta, object)):
    __slots__ = ("a", "b")


class _MixedClass(_SlottedClass):
    c = None
    d = None


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


def test_get_protected_slotted_state():
    class Class(object):
        __slots__ = ("__a", "__b")

        def __init__(self):
            self.__a = 1
            self.__b = 2

    class SubClass(Class):
        __slots__ = ("__a", "__b", "__c")

        def __init__(self):
            super(SubClass, self).__init__()
            self.__a = 3
            self.__b = 4
            self.__c = 5

    assert get_state(SubClass()) == {
        "_Class__a": 1,
        "_Class__b": 2,
        "_SubClass__a": 3,
        "_SubClass__b": 4,
        "_SubClass__c": 5,
    }


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


def test_mixed_class():
    obj = _MixedClass()
    update_state(obj, {"a": 1, "b": 2, "c": 3, "d": 4})

    assert obj.a == 1
    assert obj.b == 2
    assert obj.c == 3
    assert obj.d == 4

    pickled_obj = pickle.loads(pickle.dumps(obj))

    assert pickled_obj.a == 1
    assert pickled_obj.b == 2
    assert pickled_obj.c == 3
    assert pickled_obj.d == 4

    copied_obj = copy.copy(obj)

    assert copied_obj.a == 1
    assert copied_obj.b == 2
    assert copied_obj.c == 3
    assert copied_obj.d == 4


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


def test_reducible_class():
    assert isinstance(Reducible, ReducibleMeta)


def test_reducible_meta():
    obj = _ReducibleClass()
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
