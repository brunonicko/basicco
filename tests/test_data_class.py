import math

import pytest  # noqa

from basicco.data_class import DataClass, as_dict, as_tuple, deletes, field, fields, replace


class Vector(DataClass):
    x = field(required=False)  # type: float
    y = field()  # type: float
    name = field(eq=False, kw_only=True)  # type: str

    @property
    @field
    def mag(self):
        # type: () -> float
        return math.sqrt(self.x**2 + self.y**2)


class ImmutableVector(Vector):
    __kwargs__ = {"frozen": True}


def test_basic_data():
    vector_a = Vector(3, 4, name="vector_a")
    assert vector_a == Vector(3, 4, name="vector_b")

    assert repr(vector_a) == "Vector(3, 4, name='vector_a', mag=5.0)"

    vector_a.x = 4
    vector_a.y = 3
    assert vector_a != Vector(3, 4, "vector_a")

    assert "mag" in as_dict(vector_a)

    with pytest.raises(TypeError):
        hash(vector_a)

    assert list(fields(Vector).items()) == [
        ("x", Vector.__fields__["x"]),
        ("y", Vector.__fields__["y"]),
        ("name", Vector.__fields__["name"]),
        ("mag", Vector.__fields__["mag"]),
    ]


def test_immutable_basic_data():
    vector_m = Vector(3, 4, name="mut_vector")
    vector_m.x = 300
    vector_m.y = 400
    assert as_tuple(vector_m) == (300, 400, "mut_vector", 500)

    vector_a = ImmutableVector(3, 4, name="vector_a")
    assert vector_a == ImmutableVector(3, 4, name="vector_b")
    assert hash(vector_a) == hash(ImmutableVector(3, 4, name="vector_b"))

    assert replace(vector_a, x=30, y=40) == ImmutableVector(30, 40, name="vector_c")

    v = ImmutableVector(3, 4, name="vector_d")
    object.__delattr__(v, "x")
    assert deletes(vector_a, "x") == v

    assert list(fields(ImmutableVector).items()) == [
        ("x", ImmutableVector.__fields__["x"]),
        ("y", ImmutableVector.__fields__["y"]),
        ("name", ImmutableVector.__fields__["name"]),
        ("mag", ImmutableVector.__fields__["mag"]),
    ]


if __name__ == "__main__":
    pytest.main()
