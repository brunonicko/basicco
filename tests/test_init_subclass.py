import sys

import pytest  # noqa

from basicco.init_subclass import InitSubclassMeta, InitSubclass


def test_meta():
    assert isinstance(InitSubclass, InitSubclassMeta)


def test_init_subclass():
    class A(InitSubclass):
        __kwargs__ = {}

        def __init_subclass__(cls, foo=None, bar=None, **kwargs):
            assert cls is not A
            assert foo == "{}1".format(cls.__name__)
            assert bar == "{}2".format(cls.__name__)
            super(A, cls).__init_subclass__(**kwargs)  # noqa

    assert not hasattr(A, "__kwargs__")

    class B(A):
        __kwargs__ = {"foo": "B1", "bar": "B2"}

    assert not hasattr(B, "__kwargs__")

    class C(B):
        __kwargs__ = {"foo": "C1", "bar": "C2"}

    assert not hasattr(C, "__kwargs__")


def test_bad_base_kwargs():
    class A(object):
        __kwargs__ = {}

    with pytest.raises(TypeError):

        class B(InitSubclass, A):
            pass

        assert not B


def test_bad_base_init_subclass():
    if sys.version_info[:3] < (3, 6):

        class A(object):
            def __init_subclass__(cls, **kwargs):
                pass

        with pytest.raises(TypeError):

            class B(A, InitSubclass):
                pass

            assert not B
    else:

        class A(object):
            def __init_subclass__(cls, **kwargs):
                pass

        class B(A, InitSubclass):
            pass

        assert B


def test_newer_python():
    if sys.version_info[:3] >= (3, 6):
        code = """
class A(InitSubclass):

    def __init_subclass__(cls, foo=None, bar=None, **kwargs):
        assert cls is not A
        assert foo == "{}1".format(cls.__name__)
        assert bar == "{}2".format(cls.__name__)
        super(A, cls).__init_subclass__(**kwargs)

assert not hasattr(A, "__kwargs__")

class B(A, foo="B1"):
    __kwargs__ = {"bar": "B2"}

assert not hasattr(B, "__kwargs__")

class C(B, bar="C2"):
    __kwargs__ = {"foo": "C1"}

assert not hasattr(C, "__kwargs__")
"""
        exec(code, globals(), globals())


if __name__ == "__main__":
    pytest.main()
