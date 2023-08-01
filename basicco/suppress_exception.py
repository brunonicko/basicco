"""
Backport of :func:`contextlib.suppress`.
"""

__all__ = ["suppress_exception"]


try:
    from contextlib import suppress as suppress_exception  # noqa

except ImportError:
    from contextlib import contextmanager

    from tippo import Any, Iterator, Type

    @contextmanager
    def _suppress_exception(*exceptions):
        # type: (*Type[Exception]) -> Iterator[None]
        """
        Return a context manager that suppresses any of the specified exceptions if they
        occur in the body of a with statement and then resumes execution with the first
        statement following the end of the with statement.

        As with any other mechanism that completely suppresses exceptions, this context
        manager should be used only to cover very specific errors where silently
        continuing with program execution is known to be the right thing to do.

        :return: Null context manager.
        """
        try:
            yield
        except Exception as e:
            if not exceptions or not isinstance(e, exceptions):
                raise

    _suppress_exception.__name__ = "suppress_exception"
    _suppress_exception.__qualname__ = "suppress_exception"
    globals()["suppress_exception"] = _suppress_exception
