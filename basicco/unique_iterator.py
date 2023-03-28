"""Iterator that yields unique values."""

from tippo import Iterator, TypeVar

__all__ = ["unique_iterator"]


_T = TypeVar("_T")


def unique_iterator(iterator):
    # type: (Iterator[_T]) -> Iterator[_T]
    """
    Iterator that yields unique values.

    :param iterator: Iterator.
    :return: Unique iterator.
    """
    seen = set()
    for value in iterator:
        if value in seen:
            continue
        seen.add(value)
        yield value
