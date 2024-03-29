"""
Backport of `functools.cache`, `functools.lru_cache`, and `functools.update_wrapper`.
Based on `jaraco/backports.functools_lru_cache
<https://github.com/jaraco/backports.functools_lru_cache>`_.
"""

__all__ = ["cache", "lru_cache", "update_wrapper"]


try:
    from functools import cache, lru_cache, update_wrapper  # noqa

except ImportError:
    import functools
    from threading import RLock

    from six import integer_types
    from tippo import (
        Any,
        Callable,
        Dict,
        FrozenSet,
        List,
        Literal,
        Mapping,
        NamedTuple,
        Tuple,
        Type,
        TypeVar,
        Union,
        overload,
    )

    T = TypeVar("T")

    _CacheInfo = NamedTuple(
        "_CacheInfo",
        (
            ("hits", int),
            ("misses", int),
            ("maxsize", Union[int, None]),
            ("currsize", int),
        ),
    )

    @functools.wraps(functools.update_wrapper)
    def _update_wrapper(
        wrapper,  # type: Callable[..., T]
        wrapped,  # type: Callable[..., T]
        assigned=functools.WRAPPER_ASSIGNMENTS,  # type: Tuple[str, ...]
        updated=functools.WRAPPER_UPDATES,  # type: Tuple[str, ...]
    ):
        # type: (...) -> Callable[..., T]
        """
        Patch two bugs in functools.update_wrapper.
        """
        # workaround for http://bugs.python.org/issue3445
        assigned = tuple(attr for attr in assigned if hasattr(wrapped, attr))
        wrapper = functools.update_wrapper(wrapper, wrapped, assigned, updated)
        # workaround for https://bugs.python.org/issue17482
        wrapper.__wrapped__ = wrapped  # type: ignore
        return wrapper

    class _HashedSeq(List[Any]):
        """
        This class guarantees that hash() will be called no more than once
        per element.  This is important because the lru_cache() will hash
        the key multiple times on a cache miss.
        """

        __slots__ = "hashvalue"

        def __init__(self, tup, hash=hash):  # noqa
            # type: (Tuple[Any, ...], Callable[..., int]) -> None
            self[:] = tup
            self.hashvalue = hash(tup)

        def __hash__(self):  # type: ignore
            return self.hashvalue

    def _make_key(
        args,  # type: Tuple[Any, ...]
        kwds,  # type: Mapping[str, Any]
        typed,  # type: bool
        kwd_mark=(object(),),  # type: Tuple[object, ...]
        fasttypes=frozenset({int, str}),  # type: FrozenSet[Type[Any]]
        tuple=tuple,  # type: Type[Tuple[Any, ...]]  # noqa
        type=type,  # type: Type[Any]  # noqa
        len=len,  # type: Callable[..., int]  # noqa
    ):
        # type: (...) -> Any
        """Make a cache key from optionally typed positional and keyword arguments

        The key is constructed in a way that is flat as possible rather than
        as a nested structure that would take more memory.

        If there is only a single argument and its data type is known to cache
        its hash value, then that argument is returned without a wrapper.  This
        saves space and improves lookup speed.

        """
        # All code below relies on kwds preserving the order input by the user.
        # Formerly, we sorted() the kwds before looping. The new way is *much*
        # faster; however, it means that f(x=1, y=2) will now be treated as a
        # distinct call from f(y=2, x=1) which will be cached separately.
        key = args
        if kwds:
            key += kwd_mark
            for item in kwds.items():
                key += item
        if typed:
            key += tuple(type(v) for v in args)
            if kwds:
                key += tuple(type(v) for v in kwds.values())
        elif len(key) == 1 and type(key[0]) in fasttypes:
            return key[0]
        return _HashedSeq(key)

    @overload
    def _lru_cache(
        maxsize=128,  # type: Union[int, None]
        typed=False,  # type: bool
    ):
        # type: (...) -> Callable[[Callable[..., T]], Callable[..., T]]
        pass

    @overload
    def _lru_cache(
        maxsize,  # type: Callable[..., T]
        typed=False,  # type: Literal[False]
    ):
        # type: (...) -> Callable[..., T]
        pass

    def _lru_cache(
        maxsize=128,  # type: Any
        typed=False,  # type: Any
    ):
        # type: (...) -> Any
        """
        Least-recently-used cache decorator.

        If *maxsize* is set to None, the LRU features are disabled and the cache
        can grow without bound.

        If *typed* is True, arguments of different types will be cached separately.
        For example, f(decimal.Decimal("3.0")) and f(3.0) will be treated as
        distinct calls with distinct results. Some types such as str and int may
        be cached separately even when typed is false.

        Arguments to the cached function must be hashable.

        View the cache statistics named tuple (hits, misses, maxsize, currsize)
        with f.cache_info().  Clear the cache and statistics with f.cache_clear().
        Access the underlying function with f.__wrapped__.
        """

        # Users should only access the lru_cache through its public API:
        #       cache_info, cache_clear, and f.__wrapped__
        # The internals of the lru_cache are encapsulated for thread safety and
        # to allow the implementation to change (including a possible C version).

        if isinstance(maxsize, integer_types):
            # Negative maxsize is treated as 0.
            if maxsize < 0:
                maxsize = 0

        elif callable(maxsize) and isinstance(typed, bool):
            # The user_function was passed in directly via the maxsize argument
            user_function, maxsize = maxsize, 128
            wrapper = _lru_cache_wrapper(user_function, maxsize, typed, _CacheInfo)
            wrapper.cache_parameters = lambda: (  # type: ignore
                {"maxsize": maxsize, "typed": typed}
            )
            return _update_wrapper(wrapper, user_function)

        elif maxsize is not None:
            raise TypeError(
                "expected first argument to be an integer, a callable, or None"
            )

        def decorating_function(user_function):  # noqa
            # type: (Callable[..., T]) -> Callable[..., T]
            wrapper = _lru_cache_wrapper(  # noqa
                user_function,
                maxsize,
                typed,
                _CacheInfo,
            )
            wrapper.cache_parameters = lambda: (  # type: ignore
                {"maxsize": maxsize, "typed": typed}
            )
            return _update_wrapper(wrapper, user_function)

        return decorating_function

    def _lru_cache_wrapper(
        user_function,  # type: Callable[..., T]
        maxsize,  # type: Union[int, None]
        typed,  # type: bool
        _CacheInfo_,  # type: Type[_CacheInfo]  # noqa
    ):
        # type: (...) -> Callable[..., T]

        # Constants shared by all lru cache instances:
        sentinel = object()  # unique object used to signal cache misses
        make_key = _make_key  # build a key from the function arguments
        PREV, NEXT, KEY, RESULT = 0, 1, 2, 3  # names for the link fields  # noqa

        cache = {}  # type: Dict[Any, Any]  # noqa
        non_locals = {
            "hits": 0,
            "misses": 0,
            "full": False,
            "root": [],  # root of the circular doubly linked list
        }  # type: Dict[str, Any]
        cache_get = cache.get  # bound method to look up a key or return None
        cache_len = cache.__len__  # get cache size without calling len()
        lock = RLock()  # because linkedlist updates aren't threadsafe
        non_locals["root"][:] = [
            non_locals["root"],
            non_locals["root"],
            None,
            None,
        ]  # initialize by pointing to self

        if maxsize == 0:

            def wrapper(*args, **kwds):
                # type: (*Any, **Any) -> Any
                # No caching -- just a statistics update
                non_locals["misses"] += 1
                result = user_function(*args, **kwds)
                return result

        elif maxsize is None:

            def wrapper(*args, **kwds):
                # type: (*Any, **Any) -> Any
                # Simple caching without ordering or size limit
                key = make_key(args, kwds, typed)
                result = cache_get(key, sentinel)
                if result is not sentinel:
                    non_locals["hits"] += 1
                    return result
                non_locals["misses"] += 1
                result = user_function(*args, **kwds)
                cache[key] = result
                return result

        else:

            def wrapper(*args, **kwds):
                # type: (*Any, **Any) -> Any
                # Size limited caching that tracks accesses by recency
                key = make_key(args, kwds, typed)
                with lock:
                    link = cache_get(key)
                    if link is not None:
                        # Move the link to the front of the circular queue
                        link_prev, link_next, _key, result = link
                        link_prev[NEXT] = link_next
                        link_next[PREV] = link_prev
                        last = non_locals["root"][PREV]
                        last[NEXT] = non_locals["root"][PREV] = link
                        link[PREV] = last
                        link[NEXT] = non_locals["root"]
                        non_locals["hits"] += 1
                        return result
                    non_locals["misses"] += 1
                result = user_function(*args, **kwds)
                with lock:
                    if key in cache:
                        # Getting here means that this same key was added to the
                        # cache while the lock was released.  Since the link
                        # update is already done, we need only return the
                        # computed result and update the count of misses.
                        pass
                    elif non_locals["full"]:
                        # Use the old root to store the new key and result.
                        oldroot = non_locals["root"]
                        oldroot[KEY] = key
                        oldroot[RESULT] = result
                        # Empty the oldest link and make it the new root.
                        # Keep a reference to the old key and old result to
                        # prevent their ref counts from going to zero during the
                        # update. That will prevent potentially arbitrary object
                        # clean-up code (i.e. __del__) from running while we're
                        # still adjusting the links.
                        root = oldroot[NEXT]
                        oldkey = root[KEY]
                        root[KEY] = root[RESULT] = None
                        # Now update the cache dictionary.
                        del cache[oldkey]
                        # Save the potentially reentrant cache[key] assignment
                        # for last, after the root and links have been put in
                        # a consistent state.
                        cache[key] = oldroot
                    else:
                        # Put result in a new link at the front of the queue.
                        last = non_locals["root"][PREV]
                        link = [last, non_locals["root"], key, result]
                        last[NEXT] = non_locals["root"][PREV] = cache[key] = link
                        # Use the cache_len bound method instead of the len() function
                        # which could potentially be wrapped in a lru_cache itself.
                        assert maxsize is not None
                        non_locals["full"] = cache_len() >= maxsize
                return result

        def cache_info():
            # type: () -> _CacheInfo
            """Report cache statistics"""
            with lock:
                return _CacheInfo_(
                    non_locals["hits"],
                    non_locals["misses"],
                    maxsize,
                    cache_len(),
                )

        def cache_clear():
            # type: () -> None
            """Clear the cache and cache statistics"""
            with lock:
                cache.clear()
                non_locals["root"][:] = [
                    non_locals["root"],
                    non_locals["root"],
                    None,
                    None,
                ]
                non_locals["hits"] = non_locals["misses"] = 0
                non_locals["full"] = False

        wrapper.cache_info = cache_info  # type: ignore
        wrapper.cache_clear = cache_clear  # type: ignore
        return wrapper

    def _cache(user_function):
        # type: (Callable[..., T]) -> Callable[..., T]
        """Simple lightweight unbounded cache. Sometimes called "memoize"."""
        return _lru_cache(maxsize=None)(user_function)

    _update_wrapper.__name__ = "update_wrapper"
    globals()["update_wrapper"] = _update_wrapper

    _lru_cache.__name__ = "lru_cache"
    globals()["lru_cache"] = _lru_cache

    _cache.__name__ = "cache"
    globals()["cache"] = _cache
