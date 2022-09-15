"""Iterator that yields unique values."""

from tippo import Iterator, TypeVar

__all__ = ["unique_iterator"]


T = TypeVar("T")


def unique_iterator(iterator):
    # type: (Iterator[T]) -> Iterator[T]
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
