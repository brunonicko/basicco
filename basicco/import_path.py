"""Import from/generate lazy dot paths."""

from __future__ import absolute_import, division, print_function

import types

import six
from six import moves
import typing_inspect  # type: ignore
from tippo import TYPE_CHECKING

from .qualname import qualname

if TYPE_CHECKING:
    from tippo import Any, Iterable, Optional

__all__ = ["DEFAULT_BUILTIN_PATHS", "import_path", "extract_generic_paths", "get_name", "get_path"]


DEFAULT_BUILTIN_PATHS = (moves.builtins.__name__, "tippo")
_NOTHING = object()
_SPECIAL_VALUES = {
    "...": Ellipsis,
    "None": None,
    "NoneType": type(None),
    "True": True,
    "False": False,
    "NotImplemented": NotImplemented,
    "NotImplementedType": type(NotImplemented),
}
_SPECIAL_PATHS = {v: k for k, v in _SPECIAL_VALUES.items()}


def _import_builtin(path, builtin_paths):
    # type: (str, Iterable[str]) -> Any
    for builtin_path in builtin_paths:
        try:
            return import_path(".".join((builtin_path, path)), builtin_paths=())
        except (ImportError, AttributeError):
            continue
    return _NOTHING


def _get_generic_path(obj, generic_paths, builtin_paths):
    # type: (Any, tuple[str, ...], Iterable[str]) -> Any
    generics = tuple(import_path(gp, builtin_paths=builtin_paths) for gp in generic_paths)
    if generics:
        if len(generics) == 1:
            return obj[generics[0]]
        else:
            return obj[generics]
    else:
        return obj


def import_path(
    path,  # type: str
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,
):
    # type: (...) -> Any
    """
    Import from a dot path.

    :param path: Dot path.
    :param extra_paths: Extra module paths in fallback order.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :return: Imported module/object.
    """

    # Add extra paths to builtin paths.
    builtin_paths = tuple(extra_paths) + tuple(builtin_paths)

    # Special value.
    if path in _SPECIAL_VALUES:
        return _SPECIAL_VALUES[path]

    # Check and split dot path.
    if not path:
        raise ValueError("empty path")
    path, generic_paths = extract_generic_paths(path)
    if not generic:
        generic_paths = ()
    path_parts = path.split(".")

    # Import the module.
    module = _NOTHING
    module_path_parts = []
    for path_part in path_parts:
        module_path_parts.append(path_part)
        current_path = ".".join(module_path_parts)
        try:
            module = __import__(current_path)
        except ImportError:
            module_path_parts.pop()
            break
    if module is _NOTHING:
        builtin_obj = _import_builtin(path, builtin_paths)
        if builtin_obj is not _NOTHING:
            return _get_generic_path(builtin_obj, generic_paths, builtin_paths)
        error = "could not import module for {!r}".format(path)
        raise ImportError(error)

    # Reset the module path parts (workaround for things like six.moves).
    module_path_parts = module.__name__.split(".")  # type: ignore

    # Import the object.
    obj_path_parts = path_parts[len(module_path_parts) :]
    if not obj_path_parts:
        if generic_paths:
            error = "can't import generics {!r} for module {!r}".format(generic_paths, path)
            raise ImportError(error)
        return module
    previous_obj = module
    obj = _NOTHING
    for path_part in obj_path_parts:
        try:
            obj = previous_obj = getattr(previous_obj, path_part)
        except AttributeError:
            builtin_obj = _import_builtin(path, builtin_paths)
            if builtin_obj is not _NOTHING:
                return _get_generic_path(builtin_obj, generic_paths, builtin_paths)
            raise

    return _get_generic_path(obj, generic_paths, builtin_paths)


def extract_generic_paths(path):
    # type: (str) -> tuple[str, tuple[str, ...]]
    """
    Extract generic paths from dot path.

    :param path: Dot path.
    :return: Dot path and generic paths.
    """

    # Check if contains generic brackets.
    if any(t in path for t in ("[", "]")):

        # Separate generic paths string from import path.
        if path.count("[") != path.count("]") or not path.endswith("]"):
            error = "invalid path {!r}".format(path)
            raise ValueError(error)
        first_index = path.index("[") + 1
        stop_index = len(path) - list(reversed(path)).index("]") - 1
        generic_paths = path[first_index:stop_index]

        # Split on commas but not the ones inside brackets.
        extracted_generic_paths = []  # type: list[str]
        current_path = ""
        in_brackets = 0
        for character in generic_paths:
            if character == " ":
                continue
            if character == "[":
                in_brackets += 1
            elif character == "]":
                in_brackets -= 1
            elif character == "," and not in_brackets:
                extracted_generic_paths.append(current_path)
                current_path = ""
                continue
            current_path += character

        # Assert the correct number of levels.
        if in_brackets != 0:
            error = "invalid generic paths {!r} in {!r}".format(generic_paths, path)
            raise ValueError(error)

        # Append the rest of the string.
        if current_path:
            extracted_generic_paths.append(current_path)

        # Separate import path.
        path = path[: first_index - 1]
    else:
        extracted_generic_paths = []

    # Return extracted paths.
    return path, tuple(extracted_generic_paths)


def get_name(obj):
    # type: (Any) -> Optional[str]
    """
    Get name.

    :param obj: Type/typing form.
    :return: Name or None.
    :raises TypeError: Could not get name for typing argument.
    """
    name = None

    # Forward references.
    if hasattr(obj, "__forward_arg__"):
        name = obj.__forward_arg__

    # Special name.
    if name is None:
        try:
            if obj in _SPECIAL_PATHS:
                name = _SPECIAL_PATHS[obj]
        except TypeError:  # ignore non-hashable
            pass

    # Python 2.7.
    if not hasattr(obj, "__forward_arg__") and type(obj).__module__ in ("typing", "typing_extensions", "tippo"):
        if type(obj).__name__.strip("_") == "Literal":
            return "Literal"
        if type(obj).__name__.strip("_") == "Final":
            return "Final"
        if type(obj).__name__.strip("_") == "ClassVar":
            return "ClassVar"

    # Try a couple of ways to get the name.
    if name is None:

        # Get origin name.
        origin = typing_inspect.get_origin(obj)
        if origin is not None:
            try:
                origin_qualified_name = qualname(origin, fallback=None)
            except TypeError:
                origin_qualified_name = None
            origin_name = (
                origin_qualified_name
                or getattr(origin, "__name__", None)
                or getattr(origin, "_name", None)
                or getattr(origin, "__forward_arg__", None)
            )
        else:
            origin_name = None

        # Get the name.
        try:
            qualified_name = qualname(obj, fallback=None)
        except TypeError:
            qualified_name = None
        name = (
            qualified_name
            or getattr(obj, "__name__", None)
            or getattr(obj, "_name", None)
            or getattr(obj, "__forward_arg__", None)
        )

        # Choose the origin name if longer (for qualified generic names).
        if origin_name is not None:
            if name is not None and len(origin_name) > len(name):
                name = origin_name

            # Get the name from the origin.
            elif name is None:
                name = origin_name

    return name


def get_path(
    obj,  # type: Any
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=DEFAULT_BUILTIN_PATHS,  # type: Iterable[str]
    generic=True,  # type: bool
    check=True,  # type: bool
):
    # type: (...) -> str
    """
    Get dot path to an object or module.

    :param obj: Object or module.
    :param extra_paths: Extra module paths in fallback order.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to include path to generic as well.
    :param check: Whether to check path for consistency.
    :return: Dot path.
    """

    # Add extra paths to builtin paths.
    builtin_paths = tuple(extra_paths) + tuple(builtin_paths)

    # Module.
    if isinstance(obj, types.ModuleType):
        return obj.__name__

    # Special paths.
    if obj in _SPECIAL_PATHS:
        return _SPECIAL_PATHS[obj]

    # Get generic suffix.
    generic_suffix = ""
    generic_origin, generic_args = typing_inspect.get_origin(obj), typing_inspect.get_args(obj, evaluate=True)
    if generic_origin is not None:
        assert generic_args is not None
        if generic_args:
            generic_suffix = "".join(
                (
                    "[",
                    ", ".join(get_path(ga, builtin_paths=builtin_paths, generic=generic) for ga in generic_args),
                    "]",
                )
            )

    # Get name and module.
    try:
        if generic_origin is not None:
            module = generic_origin.__module__
        else:
            module = obj.__module__
    except AttributeError:
        error = "non-importable instance of {!r}".format(type(obj).__name__)
        exc = TypeError(error)  # type: Exception
        six.raise_from(exc, None)
        raise exc
    else:
        name = get_name(obj)
    if not module:
        error = "can't get module for {}".format(obj)
        raise AttributeError(error)
    if module in builtin_paths:
        module = ""
    if not name:
        error = "can't get name for {}".format(obj)
        raise AttributeError(error)
    if "<locals>" in name:
        error = "local name {!r} is not importable".format(name)
        raise ImportError(error)

    # Assemble path and check for consistency.
    path = ".".join(p for p in (module, name) if p)
    if generic and generic_suffix:
        path += generic_suffix
    elif not generic and generic_origin is not None:
        obj = generic_origin
    try:
        imported_obj = import_path(path, builtin_paths=builtin_paths)
        if imported_obj != obj:
            raise ImportError()
    except (ImportError, AttributeError):
        if check:
            error = "import path {!r} is not consistent for {}".format(path, obj)
            exc = ImportError(error)
            six.raise_from(exc, None)
            raise exc

    return path
