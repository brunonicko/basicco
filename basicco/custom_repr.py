"""Custom representation functions."""

from typing import Any, Callable, Hashable, Iterable, Mapping, Optional, Tuple

__all__ = ["mapping_repr", "iterable_repr"]


def mapping_repr(
    mapping: Mapping,
    prefix: str = "{",
    template: str = "{key}: {value}",
    separator: str = ", ",
    suffix: str = "}",
    sorting: bool = False,
    sort_key: Optional[Callable[[Tuple[Any, Any]], Any]] = None,
    reverse: bool = False,
    key_repr: Callable[[Any], str] = repr,
    value_repr: Callable[[Any], str] = repr,
) -> str:
    """
    Get custom representation of a mapping.

    :param mapping: Mapping.
    :param prefix: Prefix.
    :param template: Item format template ({key} and {value}).
    :param separator: Separator.
    :param suffix: Suffix.
    :param sorting: Whether to sort keys.
    :param sort_key: Sorting key.
    :param reverse: Reverse sorting.
    :param key_repr: Key representation function.
    :param value_repr: Value representation function.
    :return: Custom representation.
    """
    parts = []
    iterable: Iterable[Tuple[Hashable, Any]] = mapping.items()
    if sort_key is None:
        sort_key = lambda item: item[0]
    if sorting:
        iterable = sorted(iterable, key=sort_key, reverse=reverse)
    for key, value in iterable:
        part = template.format(key=key_repr(key), value=value_repr(value))
        parts.append(part)
    return prefix + separator.join(parts) + suffix


def iterable_repr(
    iterable: Iterable,
    prefix: str = "[",
    template: str = "{value}",
    separator: str = ", ",
    suffix: str = "]",
    sorting: bool = False,
    sort_key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
    value_repr: Callable[[Any], str] = repr,
) -> str:
    """
    Get custom representation of an iterable.

    :param iterable: Iterable.
    :param prefix: Prefix.
    :param template: Item format template ({key} and {value}).
    :param separator: Separator.
    :param suffix: Suffix.
    :param sorting: Whether to sort the iterable or not.
    :param sort_key: Sorting key.
    :param reverse: Reverse sorting.
    :param value_repr: Value representation function.
    :return: Custom representation.
    """
    parts = []
    if sorting:
        iterable = sorted(iterable, key=sort_key, reverse=reverse)
    for value in iterable:
        part = template.format(value=value_repr(value))
        parts.append(part)
    return prefix + separator.join(parts) + suffix
