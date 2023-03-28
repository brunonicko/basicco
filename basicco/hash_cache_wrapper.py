"""An integer subclass that pickles/copies as None."""

from tippo import Any, Callable, Tuple

__all__ = ["HashCacheWrapper"]


def _none_constructor():
    # type: () -> None
    return None


class HashCacheWrapper(int):
    """
    An integer subclass that pickles/copies as None.
    This can be used to avoid serializing a cached hash value.
    """

    def __copy__(self):
        # type: () -> None
        return None

    def __deepcopy__(self, memodict=None):
        # type: (Any) -> None
        return None

    def __reduce__(self):
        # type: () -> Tuple[Callable[[], None], Tuple[()]]
        return _none_constructor, ()
