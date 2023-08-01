"""
Backport of :func:`contextlib.nullcontext`.
"""

__all__ = ["null_context"]


try:
    from contextlib import nullcontext as null_context  # noqa

except ImportError:
    from contextlib import contextmanager

    from tippo import Any, Iterator, Optional, TypeVar

    T = TypeVar("T")

    @contextmanager
    def _null_context(enter_result=None):
        # type: (Optional[T]) -> Iterator[Optional[T]]
        """
        Return a context manager that returns enter_result from `__enter__`, but
        otherwise does nothing.

        :return: Null context manager.
        """
        yield enter_result

    _null_context.__name__ = "null_context"
    _null_context.__qualname__ = "null_context"
    globals()["null_context"] = _null_context
