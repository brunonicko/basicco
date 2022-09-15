"""Value factoring with support for lazy dot paths."""

import six
from tippo import Any, Callable, Iterable, Mapping, TypeVar

from .import_path import import_path

__all__ = ["fabricate_value", "format_factory"]


T = TypeVar("T")

MISSING = object()


def fabricate_value(
    factory,  # type: str | Callable | None
    value=MISSING,  # type: Any
    args=None,  # type: Iterable | None
    kwargs=None,  # type: Mapping[str, Any] | None
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=None,  # type: Iterable[str] | None
):
    # type: (...) -> Any
    """
    Pass value through the factory.

    :param factory: Factory, import path, or None.
    :param value: Input value.
    :param args: Factory arguments.
    :param kwargs: Factory keyword arguments.
    :param extra_paths: Extra module paths in fallback order.
    :param builtin_paths: Builtin module paths in fallback order.
    :return: Output value.
    :raises ValueError: Factory is None and no value was provided.
    :raises TypeError: Invalid factory type.
    """
    if isinstance(factory, six.string_types):
        factory = import_path(factory, extra_paths=extra_paths, builtin_paths=builtin_paths)
    if factory is None:
        if value is MISSING:
            error = "no value and no factory provided"
            raise ValueError(error)
        return value
    if not callable(factory):
        error = "{!r} object is not a valid callable factory".format(type(factory).__name__)
        raise TypeError(error)
    if value is MISSING:
        return factory(*args or (), **kwargs or {})
    else:
        return factory(value, *args or (), **kwargs or {})


def format_factory(factory):
    # type: (str | Callable[..., T] | None) -> str | Callable[..., T] | None
    """
    Format and check factory.

    :param factory: Factory.
    :return: Checked factory.
    """
    if factory is not None and not isinstance(factory, six.string_types) and not callable(factory):
        error = "invalid factory type {!r}, expected None, a string, or a callable".format(type(factory).__name__)
        raise TypeError(error)
    return factory
