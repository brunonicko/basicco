"""Iterator that yields unique values."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterator, TypeVar

    T = TypeVar("T")

__all__ = ["unique_iterator"]


def unique_iterator(iterator):
    # type: (Iterator[T]) -> Iterator[T]
    """
    Iterator that yields unique values.

    .. code:: python

        >>> from basicco.utils.unique_iterator import unique_iterator

        >>> list(unique_iterator([1, 2, 3, 3, 4, 4, 5]))
        [1, 2, 3, 4, 5]
    """
    seen = set()
    for value in iterator:
        if value in seen:
            continue
        seen.add(value)
        yield value
