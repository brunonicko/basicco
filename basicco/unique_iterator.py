"""Iterator that yields unique values."""

from tippo import Iterable, Iterator, TypeVar

__all__ = ["unique_iterator"]


_T = TypeVar("_T")


def unique_iterator(iterable):
    # type: (Iterable[_T]) -> Iterator[_T]
    """
    Iterator that yields unique values.

    :param iterable: Iterable.
    :return: Unique iterator.
    """
    seen = set()
    for value in iterable:
        if value in seen:
            continue
        seen.add(value)
        yield value
