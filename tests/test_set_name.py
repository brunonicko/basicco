import sys

import pytest  # noqa

from basicco.set_name import SetName, SetNameMeta


class Attribute(object):
    def __set_name__(self, owner, name):
        assert name == "attribute_{}".format(owner.__name__.lower())
        self.owner = owner
        self.name = name


def test_meta():
    assert isinstance(SetName, SetNameMeta)


def test_set_name():
    class A(SetName):
        attribute_type_a = Attribute
        attribute_a = Attribute()

    class B(A):
        attribute_type_b = Attribute
        attribute_b = Attribute()

    class C(B):
        attribute_type_c = Attribute
        attribute_c = Attribute()

    assert C.attribute_a.name == "attribute_a"
    assert C.attribute_b.name == "attribute_b"
    assert C.attribute_c.name == "attribute_c"

    assert C.attribute_a.owner == A
    assert C.attribute_b.owner == B
    assert C.attribute_c.owner == C


def test_newer_python():
    if sys.version_info[:3] >= (3, 6):
        code = """
class A(SetName):
    attribute_type_a = Attribute
    attribute_a = Attribute()

class B(A):
    attribute_type_b = Attribute
    attribute_b = Attribute()

class C(B):
    attribute_type_c = Attribute
    attribute_c = Attribute()

assert C.attribute_a.name == "attribute_a"
assert C.attribute_b.name == "attribute_b"
assert C.attribute_c.name == "attribute_c"

assert C.attribute_a.owner == A
assert C.attribute_b.owner == B
assert C.attribute_c.owner == C
"""
        exec(code, globals(), globals())


if __name__ == "__main__":
    pytest.main()
