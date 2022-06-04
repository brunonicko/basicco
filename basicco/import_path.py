"""Import from/generate lazy dot paths."""

from typing import Any, Iterable, Tuple, List, Optional, Type

__all__ = ["import_path", "extract_generic_paths", "get_path"]


_BUILTINS = ("builtins", "typing")
_NOTHING = object()
_SPECIAL_VALUES = {
    "...": ...,
    "None": None,
    "NoneType": type(None),
    "True": True,
    "False": False,
    "NotImplemented": NotImplemented,
    "NotImplementedType": type(NotImplemented),
}
_SPECIAL_PATHS = {v: k for k, v in _SPECIAL_VALUES.items()}


def _import_builtin(path: str, builtin_paths: Iterable[str]):
    for builtin_path in builtin_paths:
        try:
            return import_path(".".join((builtin_path, path)), builtin_paths=())
        except (ImportError, AttributeError):
            continue
    return _NOTHING


def _get_generic(obj: Any, generic_paths: Tuple[str, ...], builtin_paths: Iterable[str]) -> Any:
    generics = tuple(import_path(gp, builtin_paths=builtin_paths) for gp in generic_paths)
    if generics:
        if len(generics) == 1:
            return obj[generics[0]]
        else:
            return obj[generics]
    else:
        return obj


def _get_alias_origin(obj: Any) -> Tuple[Optional[Type], Optional[Tuple[Any, ...]]]:
    if getattr(obj, "__origin__", None) is not None and getattr(obj, "__args__", None) is not None:
        return obj.__origin__, obj.__args__
    else:
        return None, None


def import_path(path: str, builtin_paths: Iterable[str] = _BUILTINS, generic: bool = True) -> Any:
    """
    Import from a dot path.

    :param path: Dot path.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to import generic.
    :return: Imported module/object.
    """

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
            return _get_generic(builtin_obj, generic_paths, builtin_paths)
        raise ImportError(f"could not import module for {path!r}")

    # Import the object.
    obj_path_parts = path_parts[len(module_path_parts) :]
    if not obj_path_parts:
        if generic_paths:
            raise ImportError(f"can't import generics {generic_paths!r} for module {path!r}")
        return module
    previous_obj = module
    obj = _NOTHING
    for path_part in obj_path_parts:
        try:
            obj = previous_obj = getattr(previous_obj, path_part)
        except AttributeError:
            builtin_obj = _import_builtin(path, builtin_paths)
            if builtin_obj is not _NOTHING:
                return _get_generic(builtin_obj, generic_paths, builtin_paths)
            raise

    return _get_generic(obj, generic_paths, builtin_paths)


def extract_generic_paths(path: str) -> Tuple[str, Tuple[str, ...]]:
    """
    Extract generic paths from dot path.

    :param path: Dot path.
    :return: Dot path and generic paths.
    """

    # Check if contains generic brackets.
    if any(t in path for t in ("[", "]")):

        # Separate generic paths string from import path.
        if path.count("[") != path.count("]") or not path.endswith("]"):
            raise ValueError(f"invalid path {path!r}")
        first_index = path.index("[") + 1
        stop_index = len(path) - list(reversed(path)).index("]") - 1
        generic_paths = path[first_index:stop_index]

        # Split on commas but not the ones inside brackets.
        extracted_generic_paths: List[str] = []
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
            raise ValueError(f"invalid generic paths {generic_paths!r} in {path!r}")

        # Append the rest of the string.
        if current_path:
            extracted_generic_paths.append(current_path)

        # Separate import path.
        path = path[: first_index - 1]
    else:
        extracted_generic_paths = []

    # Return extracted paths.
    return path, tuple(extracted_generic_paths)


def get_path(
    obj,
    builtin_paths: Iterable[str] = _BUILTINS,
    generic: bool = True,
    check: bool = True,
) -> str:
    """
    Get dot path to an object or module.

    :param obj: Object or module.
    :param builtin_paths: Builtin module paths in fallback order.
    :param generic: Whether to include path to generic as well.
    :param check: Whether to check path for consistency.
    :return: Dot path.
    """

    # Special paths.
    if obj in _SPECIAL_PATHS:
        return _SPECIAL_PATHS[obj]

    # Get generic suffix.
    generic_suffix: str = ""
    generic_origin, generic_args = _get_alias_origin(obj)
    if generic_origin is not None:
        assert generic_args is not None
        generic_suffix = "".join(
            (
                "[",
                ", ".join(get_path(ga, builtin_paths=builtin_paths, generic=generic) for ga in generic_args),
                "]",
            )
        )

    # Get qualified name and module.
    try:
        if generic_origin is not None:
            module, qualified_name = (
                generic_origin.__module__,
                generic_origin.__qualname__,
            )
        else:
            module, qualified_name = obj.__module__, obj.__qualname__
    except AttributeError:
        raise TypeError(f"non-importable instance of {type(obj).__name__!r}") from None
    if not module:
        raise AttributeError(f"can't get module for {obj}")
    if module in builtin_paths:
        module = ""
    if not qualified_name:
        raise AttributeError(f"can't get qualified name for {obj}")
    if "<locals>" in qualified_name:
        raise AttributeError(f"local name {qualified_name!r} is not importable")

    # Assemble path and check for consistency.
    path = ".".join(p for p in (module, qualified_name) if p)
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
            raise ImportError(f"import path {path!r} is not consistent for {obj}") from None

    return path
