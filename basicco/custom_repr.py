"""Custom representation functions."""

from __future__ import absolute_import, division, print_function

from tippo import TYPE_CHECKING

if TYPE_CHECKING:
    from tippo import Any, Callable, Hashable, Iterable, Mapping

__all__ = ["mapping_repr", "iterable_repr"]


def mapping_repr(
    mapping,  # type: Mapping
    prefix="{",  # type: str
    template="{key}{value}",  # type: str
    separator=", ",  # type: str
    suffix="}",  # type: str
    sorting=False,  # type: bool
    sort_key=None,  # type: Callable[[tuple[Any, Any]], Any] | None
    reverse=False,  # type: bool
    key_repr=repr,  # type: Callable[[Any], str]
    value_repr=repr,  # type: Callable[[Any], str]
):
    # type: (...) -> str
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
    iterable = mapping.items()  # type: Iterable[tuple[Hashable, Any]]
    if sort_key is None:
        sort_key = lambda item: item[0]
    if sorting:
        iterable = sorted(iterable, key=sort_key, reverse=reverse)
    for key, value in iterable:
        part = template.format(key=key_repr(key), value=value_repr(value))
        parts.append(part)
    return prefix + separator.join(parts) + suffix


def iterable_repr(
    iterable,  # type: Iterable
    prefix="[",  # type: str
    template="{value}",  # type: str
    separator=", ",  # type: str
    suffix="]",  # type: str
    sorting=False,  # type: bool
    sort_key=None,  # type: Callable[[Any], Any] | None
    reverse=False,  # type: bool
    value_repr=repr,  # type: Callable[[Any], str]
):
    # type: (...) -> str
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
