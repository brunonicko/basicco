import math

import pytest  # noqa

from basicco.basic_data import BasicData, ImmutableBasicData, ItemUsecase


class VectorMixin(object):
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name

    def to_items(self, usecase=None):
        items = [("x", self.x), ("y", self.y)]
        if usecase in (ItemUsecase.INIT, ItemUsecase.REPR, None):
            items.append(("name", self.name))
            if usecase is ItemUsecase.REPR:
                items.append(("mag", self.mag))
        return items

    @property
    def mag(self):
        return math.sqrt(self.x**2 + self.y**2)


class Vector(VectorMixin, BasicData):
    pass


class ImmutableVector(VectorMixin, ImmutableBasicData):
    def update(self, *args, **kwargs):
        init_args = self.to_dict(ItemUsecase.INIT)
        init_args.update(*args, **kwargs)
        return type(self)(**init_args)  # type: ignore


def test_basic_data():
    vector_a = Vector(3, 4, "vector_a")
    assert vector_a == Vector(3, 4, "vector_b")

    assert repr(vector_a) == "Vector(x=3, y=4, name='vector_a', <mag=5.0>)"

    vector_a.x = 4
    vector_a.y = 3
    assert vector_a != Vector(3, 4, "vector_a")

    assert "name" in vector_a.to_dict()
    for usecase in (ItemUsecase.EQ, ItemUsecase.HASH):
        assert "name" not in vector_a.to_dict(usecase)

    with pytest.raises(TypeError):
        hash(vector_a)


def test_immutable_basic_data():
    vector_a = ImmutableVector(3, 4, "vector_a")
    assert vector_a == ImmutableVector(3, 4, "vector_b")

    assert vector_a.update(x=4, y=3) != ImmutableVector(3, 4, "vector_a")
    assert vector_a.update(x=4, y=3) == ImmutableVector(4, 3, "vector_x")

    assert hash(vector_a) == hash(tuple(vector_a.to_items(ItemUsecase.HASH)))


if __name__ == "__main__":
    pytest.main()
