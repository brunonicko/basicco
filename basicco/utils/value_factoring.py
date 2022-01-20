"""Value factoring with support for lazy import paths."""

from typing import TYPE_CHECKING

from six import string_types

from .import_path import format_import_path, import_from_path

if TYPE_CHECKING:
    from typing import Any, Callable, Optional, Union, Iterable, Mapping

__all__ = ["format_factory", "import_factory", "fabricate_value"]


def format_factory(
    factory,  # type: Union[Callable, Optional[str]]
    default_module=None,  # type: Optional[str]
    builtin_modules=None,  # type: Optional[str]
):
    # type: (...) -> Union[Callable, Optional[str]]
    """
    Validate a factory, add a module path if missing one, resolve relative paths.

    :param factory: Factory, import path, or None.
    :type factory: callable or str or None

    :param default_module: Default module path (for paths without a module).
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: Validated factory.
    :rtype: callable or str or None

    :raises TypeError: Invalid factory type.
    """
    if factory is None or callable(factory):
        return factory
    elif isinstance(factory, string_types):
        return format_import_path(
            factory, default_module=default_module, builtin_modules=builtin_modules
        )
    error = "{} object is not a callable factory".format(type(factory).__name__)
    raise TypeError(error)


def import_factory(
    factory,  # type: Union[Callable, Optional[str]]
    default_module=None,  # type: Optional[str]
    builtin_modules=None,  # type: Optional[str]
):
    # type: (...) -> Optional[Callable]
    """
    Import factory.

    :param factory: Factory, import path, or None.
    :type factory: callable or str or None

    :param default_module: Module path.
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: Imported factory.
    :rtype: callable or None

    :raises TypeError: Invalid factory type.
    """
    if factory is None or callable(factory):
        return factory
    elif isinstance(factory, string_types):
        return import_from_path(
            factory, default_module=default_module, builtin_modules=builtin_modules
        )
    error = "{} object is not a callable factory".format(type(factory).__name__)
    raise TypeError(error)


def fabricate_value(
    factory,  # type: Union[Callable, Optional[str]]
    value,  # type: Any
    args=None,  # type: Optional[Iterable]
    kwargs=None,  # type: Optional[Mapping[str, Any]]
    default_module=None,  # type: Optional[str]
    builtin_modules=None,  # type: Optional[str]
):
    # type: (...) -> Any
    """
    Pass value through the factory.

    :param factory: Factory, import path, or None.
    :type factory: callable or str or None

    :param value: Input value.

    :param args: Factory arguments.
    :type args: list or None

    :param kwargs: Factory keyword arguments.
    :type kwargs: dict[str, Any] or None

    :param default_module: Module path.
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: Output value.

    :raises TypeError: Invalid factory type.
    """
    factory = import_factory(
        factory, default_module=default_module, builtin_modules=builtin_modules
    )
    if factory is not None:
        return factory(value, *args or (), **kwargs or {})
    else:
        return value
