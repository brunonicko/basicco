"""An integer subclass that pickles/copies as None."""

__all__ = ["HashCacheWrapper"]


def _none_constructor():
    return None


class HashCacheWrapper(int):
    """An integer subclass that pickles/copies as None. This can be used to avoid serializing a cached hash value."""

    def __copy__(self):
        return None

    def __deepcopy__(self, memodict=None):
        return None

    def __reduce__(self):
        return _none_constructor, ()
