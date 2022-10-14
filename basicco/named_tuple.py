"""Named tuple utilities."""

import functools

__all__ = ["defaults"]


_MISSING = object()


def _check_missing_decorator(new_method):
    @functools.wraps(new_method)
    def decorated(*args, **kwargs):
        self = new_method(*args, **kwargs)
        missing_fields = [f for f in type(self)._fields if getattr(self, f) is _MISSING]  # noqa
        for field in type(self)._fields:  # noqa
            if getattr(self, field) is _MISSING:
                error = "{}.__new__() missing {} required positional argument{}: {}".format(
                    type(self).__name__,
                    len(missing_fields),
                    "s" if len(missing_fields) > 1 else "",
                    ", ".join(repr(f) for f in missing_fields),
                )
                raise TypeError(error)
        return self

    return decorated


def defaults(**values):
    """
    Sets default values for named tuple classes.

    :param values: Default values.
    :return: Decorator that adds default values to a named tuple class.
    """

    def decorator(cls):
        if values:
            kw = None
            for field in cls._fields:
                if field in values:
                    kw = field
                elif kw is not None:
                    error = "positional field {!r} after default field {!r}".format(field, kw)
                    raise TypeError(error)
            cls.__new__.__defaults__ = (_MISSING,) * len(cls._fields)
            prototype = cls(**values)
            cls.__new__.__defaults__ = tuple(prototype)
            type.__setattr__(cls, "__new__", staticmethod(_check_missing_decorator(cls.__new__)))
        return cls

    return decorator
