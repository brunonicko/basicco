"""Import from/generate lazy dot paths."""

import types

import six
import tippo
from six import moves
from tippo import Any, Iterable, Optional

from .qualname import QualnameError, qualname

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
    builtin_paths=None,  # type: Iterable[str] | None
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

    # Default builtin paths.
    if builtin_paths is None:
        builtin_paths = DEFAULT_BUILTIN_PATHS

    # Special value.
    if path in _SPECIAL_VALUES:
        return _SPECIAL_VALUES[path]

    # Strings.
    if path.startswith("'") and path.endswith("'") or path.startswith('"') and path.endswith('"'):
        return str(path[1:-1])

    # Integers.
    if path.isdigit():
        return int(path)

    # Floats.
    if path.replace(".", "").isdigit():
        return float(path)

    # Add extra paths to builtin paths.
    builtin_paths = tuple(extra_paths) + tuple(builtin_paths)

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


def _get_qualname(obj):
    try:
        return qualname(obj)
    except (QualnameError, TypeError):
        return None


def get_name(obj):
    # type: (Any) -> Optional[str]
    """
    Get importable name.

    :param obj: Object.
    :return: Name or None.
    """
    return tippo.get_name(obj, qualname_getter=_get_qualname)


def get_path(
    obj,  # type: Any
    extra_paths=(),  # type: Iterable[str]
    builtin_paths=None,  # type: Iterable[str] | None
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

    # Default builtin paths.
    if builtin_paths is None:
        builtin_paths = DEFAULT_BUILTIN_PATHS

    # Add extra paths to builtin paths.
    builtin_paths = tuple(extra_paths) + tuple(builtin_paths)

    # Module.
    if isinstance(obj, types.ModuleType):
        return obj.__name__

    # Special paths.
    if obj in _SPECIAL_PATHS:
        return _SPECIAL_PATHS[obj]

    # Forward references.
    if isinstance(obj, tippo.ForwardRef):
        return repr(obj.__forward_arg__)

    # Strings, integers, floats.
    # noinspection PyTypeChecker
    if isinstance(obj, six.string_types + (int, float)):
        return repr(obj)

    # Get generic origin and args.
    generic_suffix = ""
    generic_origin, generic_args = tippo.get_origin(obj), tippo.get_args(obj)
    if generic and generic_origin is not None:

        # Remap from collections.abc to typing.
        if (
            getattr(obj, "__module__", None) == "typing"
            and getattr(generic_origin, "__module__", None) == "collections.abc"
        ):
            generic_origin_name = get_name(generic_origin)
            if generic_origin_name is not None and hasattr(tippo, generic_origin_name):
                generic_origin = getattr(tippo, generic_origin_name)

        # Add generic arguments to the path.
        if generic_args:
            generic_suffix = "".join(
                (
                    "[",
                    ", ".join(get_path(ga, builtin_paths=builtin_paths, check=check) for ga in generic_args),
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

    # Assemble path.
    path = ".".join(p for p in (module, name) if p)
    if generic and generic_suffix:
        path += generic_suffix
    elif not generic and generic_origin is not None:
        obj = generic_origin

    # Check for consistency.
    if check:
        try:
            imported_obj = import_path(path, builtin_paths=builtin_paths)
            if imported_obj != obj:
                raise ImportError()
        except (ImportError, AttributeError):
            error = "import path {!r} is not consistent for {}".format(path, obj)
            exc = ImportError(error)
            six.raise_from(exc, None)
            raise exc

    return path
