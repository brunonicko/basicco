__all__ = [
    "ExplicitHashMeta",
]


class ExplicitHashMeta(type):
    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):

        # Force '__hash__' to be declared when '__eq__' is declared (be explicit).
        if "__eq__" in dct and "__hash__" not in dct:
            error = ("declared '__eq__' in '{}', but didn't declare '__hash__'").format(
                name
            )
            raise TypeError(error)

        return super(ExplicitHashMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
