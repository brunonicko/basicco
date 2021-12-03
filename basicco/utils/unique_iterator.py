"""Iterator that yields unique values."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterator, TypeVar

    T = TypeVar("T")

__all__ = ["unique_iterator"]


def unique_iterator(iterator):
    # type: (Iterator[T]) -> Iterator[T]
    seen = set()
    for value in iterator:
        if value in seen:
            continue
        seen.add(value)
        yield value
