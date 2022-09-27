"""Custom representation functions."""

from tippo import Any, Callable, Iterable, Mapping

__all__ = ["mapping_repr", "iterable_repr"]


def mapping_repr(
    mapping,  # type: Mapping | Iterable[tuple[Any, Any]]
    prefix="{",  # type: str
    template="{key}: {value}",  # type: str | Callable[..., str]
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
    Get custom representation of a mapping/items.

    :param mapping: Mapping.
    :param prefix: Prefix.
    :param template: Item format template or callable (supports {key}, {value}, {i}).
    :param separator: Separator.
    :param suffix: Suffix.
    :param sorting: Whether to sort keys.
    :param sort_key: Sorting key.
    :param reverse: Reverse sorting.
    :param key_repr: Key representation function.
    :param value_repr: Value representation function.
    :return: Custom representation.
    """
    if isinstance(mapping, Mapping):
        iterable = mapping.items()  # type: Iterable[tuple[Any, Any]]
    else:
        iterable = mapping

    if sort_key is None:
        sort_key = lambda item: item[0]
    if sorting:
        iterable = sorted(iterable, key=sort_key, reverse=reverse)

    if not callable(template):
        template = lambda _template=template, **v: _template.format(**v)

    parts = []  # type: list[str]
    for i, (key, value) in enumerate(iterable):
        part = template(key=key_repr(key), value=value_repr(value), i=i)
        parts.append(part)

    return prefix + separator.join(parts) + suffix


def iterable_repr(
    iterable,  # type: Iterable
    prefix="[",  # type: str
    template="{value}",  # type: str | Callable[..., str]
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
    :param template: Item format template or callable (supports {value}, {i}).
    :param separator: Separator.
    :param suffix: Suffix.
    :param sorting: Whether to sort the iterable or not.
    :param sort_key: Sorting key.
    :param reverse: Reverse sorting.
    :param value_repr: Value representation function.
    :return: Custom representation.
    """
    if sorting:
        iterable = sorted(iterable, key=sort_key, reverse=reverse)

    if not callable(template):
        template = lambda _template=template, **v: _template.format(**v)

    parts = []  # type: list[str]
    for i, value in enumerate(iterable):
        part = template(value=value_repr(value), i=i)
        parts.append(part)

    return prefix + separator.join(parts) + suffix
