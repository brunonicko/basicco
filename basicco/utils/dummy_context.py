"""Dummy context manager."""

from contextlib import contextmanager

__all__ = ["dummy_context"]


@contextmanager
def dummy_context():
    """
    Dummy context manager.

    .. code:: python

        >>> from basicco.utils.dummy_context import dummy_context

        >>> with dummy_context():
        ...     pass
    """
    yield
