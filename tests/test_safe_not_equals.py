import pytest

from basicco.safe_not_equals import SafeNotEquals, SafeNotEqualsMeta


def test_class():
    assert isinstance(SafeNotEquals, SafeNotEqualsMeta)


def test_metaclass():
    obj_a = SafeNotEquals()
    obj_b = SafeNotEquals()
    assert (obj_a == obj_a) is not (obj_a != obj_a)
    assert (obj_b == obj_b) is not (obj_b != obj_b)
    assert (obj_a == obj_b) is not (obj_a != obj_b)


if __name__ == "__main__":
    pytest.main()
