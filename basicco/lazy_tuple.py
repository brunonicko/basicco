"""Lazily evaluated tuple."""

import types

from six.moves import collections_abc
from tippo import Any, Generic, Iterator, List, Tuple, TypeVar, overload

from ._bases import SlottedBase

__all__ = ["LazyTuple"]


_T = TypeVar("_T")


class LazyTuple(SlottedBase, Generic[_T]):
    """Lazy tuple-like structure based on a generator."""

    __slots__ = ("__generator", "__values", "__done")

    def __init__(self, generator):
        # type: (Iterator[_T]) -> None
        """
        :param generator: Value generator.
        """
        self.__generator = (
            iter(generator)
            if not isinstance(generator, types.GeneratorType)
            else generator
        )
        self.__values = []  # type: List[_T]
        self.__done = False  # type: bool

    def __hash__(self):
        # type: () -> int
        """
        Get hash.

        :return: Hash.
        """
        return hash(tuple(self))

    def __eq__(self, other):
        # type: (object) -> bool
        """
        Compare for equality.

        :param other: Other.
        :return: True if equal.
        """
        try:
            return tuple(other) == tuple(self)  # type: ignore  # noqa
        except TypeError:
            return NotImplemented

    def __ne__(self, other):
        # type: (object) -> bool
        """
        Compare for inequality.

        :param other: Other.
        :return: True if not equal
        """
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    def __repr__(self):
        # type: () -> str
        """
        Get representation.

        :return: Representation.
        """
        return "({})".format(
            ", ".join(
                [repr(v) for v in self.__values] + ([] if self.__done else ["..."])
            )
        )

    def __str__(self):
        # type: () -> str
        """
        Get string representation.

        :return: String representation.
        """
        return self.__repr__()

    @overload
    def __getitem__(self, index):
        # type: (int) -> _T
        pass

    @overload
    def __getitem__(self, index):
        # type: (slice) -> Tuple[_T, ...]
        pass

    def __getitem__(self, index):
        # type: (Any) -> Any
        """
        Get value/values at index/slice.

        :param index: Index or slice.
        :return: Value or values.
        """
        if isinstance(index, slice):
            if (
                (index.step is None or index.step > 0)
                and (index.start is None or index.start >= 0)
                and (index.stop is not None and index.stop >= 0)
            ):
                values = []
                for index_ in range(index.start or 0, index.stop, index.step or 1):
                    try:
                        values.append(self.__get(index_))
                    except IndexError:
                        break
                return tuple(values)
            else:
                self.__values.extend(self.__generator)
                self.__done = True
                return tuple(self.__values)[index]
        else:
            return self.__get(index)

    def __iter__(self):
        # type: () -> Iterator[_T]
        """
        Iterate over values.

        :return: Value iterator.
        """
        index = 0
        while True:
            try:
                yield self.__get(index)
            except IndexError:
                break
            index += 1

    def __len__(self):
        # type: () -> int
        """
        Get value count.

        :return: Value count.
        """
        self.__values.extend(self.__generator)
        self.__done = True
        return len(self.__values)

    def __get(self, index):
        # type: (int) -> _T
        """
        Get value at index.

        :param index: Index.
        :return: Value.
        """
        original_index = index

        # Resolve negative index.
        if index < 0:
            index += len(self)
        if index < 0:
            raise IndexError(original_index)

        # Get current value count, return if we already have a value.
        value_count = len(self.__values)
        if index < value_count:
            return self.__values[index]

        # Loop through the generator to get more values until we reach the index.
        for value in self.__generator:
            self.__values.append(value)
            value_count += 1
            if index < value_count:
                return self.__values[index]
        self.__done = True

        # Did not reach index, out of range.
        raise IndexError(original_index)


collections_abc.Sequence.register(LazyTuple)  # noqa
