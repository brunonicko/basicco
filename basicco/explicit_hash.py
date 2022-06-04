"""Metaclass that forces `__hash__` to be declared when `__eq__` is declared."""

__all__ = ["ExplicitHashMeta"]


class ExplicitHashMeta(type):
    """Metaclass that forces `__hash__` to be declared when `__eq__` is declared."""

    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):
        if "__eq__" in dct and "__hash__" not in dct:
            raise TypeError(f"declared '__eq__' in {name!r} but didn't declare '__hash__'")
        return super(ExplicitHashMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
