"""Dummy context manager."""

from contextlib import contextmanager

__all__ = ["dummy_context"]


@contextmanager
def dummy_context():
    """
    Dummy context manager.

    .. code:: python

        >>> from threading import RLock
        >>> from basicco.utils.dummy_context import dummy_context
        >>> lock = RLock()
        >>> def do_something(thread_safe=True):
        ...     with lock if thread_safe else dummy_context():
        ...         print("did something")
        ...
        >>> do_something(thread_safe=False)
        did something
    """
    yield
