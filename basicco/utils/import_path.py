"""Generate import paths like `module.module|Class.Class` and import from them."""

import inspect
from traceback import print_exc
from re import compile as re_compile
from typing import TYPE_CHECKING

from six import string_types, raise_from
from six.moves import builtins

from .qualified_name import QualnameError, get_qualified_name

if TYPE_CHECKING:
    from typing import Any, Optional, Tuple, List, Union, Iterable, Type

__all__ = [
    "MODULE_SEPARATOR",
    "IMPORT_PATH_MODULE_REGEX",
    "IMPORT_PATH_NAME_REGEX",
    "extract_generic_paths",
    "format_builtin_modules",
    "format_import_path",
    "import_from_path",
    "get_import_path",
]


MODULE_SEPARATOR = "|"
"""Single character that separates the module from the name."""

IMPORT_PATH_MODULE_REGEX = re_compile(r"^([\w]+[\w.]*?)$")
"""Regex to validate the module."""

IMPORT_PATH_NAME_REGEX = re_compile(r"^([\w.]+)$")
"""Regex to validate the name."""


def extract_generic_paths(import_path):
    # type: (str) -> Tuple[str, Tuple[str, ...]]
    """
    Extract generic paths from import path.

    :param import_path: Import path.
    :type import_path: str

    :return: Import path and generic paths.
    :rtype: tuple[str, tuple[str]]
    """

    # Check if contains generic brackets.
    if any(t in import_path for t in ("[", "]")):

        # Contains generic brackets, separate generic paths string from import path.
        if import_path.count("[") != import_path.count("]") or not import_path.endswith(
            "]"
        ):
            error = "invalid import path {}".format(repr(import_path))
            raise ValueError(error)
        first_index = import_path.index("[") + 1
        stop_index = len(import_path) - list(reversed(import_path)).index("]") - 1
        generic_paths = import_path[first_index:stop_index]

        # Split on commas but not the ones inside brackets.
        extracted_generic_paths = []  # type: List[str]
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
            error = "invalid generic paths {} in {}".format(
                repr(generic_paths), repr(import_path)
            )
            raise ValueError(error)

        # Append the rest of the string.
        if current_path:
            extracted_generic_paths.append(current_path)

        # Separate import path.
        import_path = import_path[: first_index - 1]
    else:
        extracted_generic_paths = []

    # Return extracted paths.
    return import_path, tuple(extracted_generic_paths)


def format_builtin_modules(builtin_modules=None):
    # type: (Optional[Union[str, Iterable[str]]]) -> Tuple[str, ...]
    """
    Validate and format built-in module paths.

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: Formatted built-in paths.
    :rtype: tuple[str]

    :raises ImportError: Invalid built-in module path.
    """

    # Default values, force into a tuple.
    if builtin_modules is None:
        builtin_modules = (builtins.__name__,)
    elif isinstance(builtin_modules, string_types):
        builtin_modules = (builtin_modules,)
    else:
        builtin_modules = tuple(builtin_modules)

    # Make sure they are importable.
    for builtin_module in builtin_modules:
        __import__(builtin_module)

    return builtin_modules


def format_import_path(import_path, default_module=None, builtin_modules=None):
    # type: (str, Optional[str], Optional[Union[str, Iterable[str]]]) -> str
    """
    Validate an import path, add a module path if missing one, resolve relative paths.

    :param import_path: Import path.
    :type import_path: str

    :param default_module: Default module path (for paths without a module).
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: Formatted and validated import path.
    :rtype: str

    :raises ValueError: Invalid import path.
    """

    # Extract generic paths away from import path.
    import_path, extracted_generic_paths = extract_generic_paths(import_path)

    # Format builtin modules.
    builtin_modules = format_builtin_modules(builtin_modules)

    # Check for module separator, ignore if is a builtin.
    if MODULE_SEPARATOR not in import_path:
        if not import_path:
            error = "empty import path"
            raise ValueError(error)
        if not any(
            hasattr(__import__(bm), import_path.split(".")[0]) for bm in builtin_modules
        ):
            if default_module is not None:
                import_path = MODULE_SEPARATOR.join((default_module, import_path))
            else:
                error = (
                    "import path {} does not specify a module name (missing {} "
                    "separator between module path and qualified name)"
                ).format(repr(import_path), repr(MODULE_SEPARATOR))
                raise ValueError(error)
    elif import_path.count(MODULE_SEPARATOR) > 1:
        error = "more than one module separator in import path {}".format(
            repr(import_path)
        )
        raise ValueError(error)

    # Split module and qualified name on the separator.
    if MODULE_SEPARATOR not in import_path:
        module, qual_name = None, import_path  # type: Optional[str], str
    else:
        module, qual_name = import_path.split(MODULE_SEPARATOR)

        # Ommit module from path if is a built-in.
        if module in builtin_modules:
            module = None

    # Match against regexes.
    if module is not None and not IMPORT_PATH_MODULE_REGEX.match(module):
        error = "invalid module path {}".format(repr(module))
        raise ValueError(error)

    if not IMPORT_PATH_NAME_REGEX.match(qual_name):
        if qual_name.startswith("."):
            error = (
                "relative import path {} does not specify a module name (missing {} "
                "separator between module path and qualified name)"
            ).format(repr(import_path), repr(MODULE_SEPARATOR))
            raise ValueError(error)
        else:
            error = "invalid qualified name {}".format(repr(qual_name))
            raise ValueError(error)

    # Resolve relative paths.
    if qual_name.startswith("."):
        assert module is not None
        qual_name = qual_name[1:]
        while qual_name.startswith("."):
            qual_name = qual_name[1:]
            if "." not in module:
                error = (
                    "relative path error; can't parse parent module for {} in path {}"
                ).format(repr(module), repr(import_path))
                raise ValueError(error)
            module = ".".join(module.split(".")[:-1])

    # Add formatted generic paths back to the qualified name.
    formatted_generic_paths = [
        format_import_path(p, default_module=default_module)
        for p in extracted_generic_paths
    ]  # type: List[str]
    if formatted_generic_paths:
        qual_name += "[" + ", ".join(formatted_generic_paths) + "]"

    # Join module and qualified name together and return formatted path.
    if module is None:
        return qual_name
    else:
        return MODULE_SEPARATOR.join((module, qual_name))


def import_from_path(import_path, default_module=None, builtin_modules=None):
    # type: (str, Optional[str], Optional[Union[str, Iterable[str]]]) -> Any
    """
    Import from import path.

    :param import_path: Import path.
    :type import_path: str

    :param default_module: Module path.
    :type default_module: str or None

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: Class, function, method, or alias.
    :rtype: type or function or alias
    """

    # Format import path.
    import_path = format_import_path(
        import_path, default_module=default_module, builtin_modules=builtin_modules
    )

    # Format built-in modules.
    builtin_modules = format_builtin_modules(builtin_modules)

    # Extract generic paths.
    import_path, extracted_generic_paths = extract_generic_paths(import_path)

    # Get module and qualified name.
    if MODULE_SEPARATOR in import_path:
        module, qual_name = import_path.split(MODULE_SEPARATOR)
    else:
        qual_name = import_path
        for builtin_module in builtin_modules:
            if hasattr(__import__(builtin_module), qual_name.split(".")[0]):
                module = builtin_module
                break
        else:
            error = "failed to match with built-in module contents"
            raise AssertionError(error)

    # Import and get object from module.
    name_parts = qual_name.split(".")
    module_obj = __import__(module, fromlist=[name_parts[0]])
    obj = module_obj
    for name_part in name_parts:
        obj = getattr(obj, name_part)

    # Import generic paths and get specific object.
    imported_generics = tuple(
        import_from_path(
            p, default_module=default_module, builtin_modules=builtin_modules
        )
        for p in extracted_generic_paths
    )
    if imported_generics:
        if len(imported_generics) == 1:
            obj = obj[imported_generics[0]]
        else:
            obj = obj[imported_generics]
    return obj


def _get_alias_origin_and_args(obj):
    # type: (Any) -> Tuple[Optional[Type], Optional[Tuple[Any, ...]]]
    """
    Get alias origin and arguments.
    If didn't provide an alias, return a tuple with two None values.

    :param obj: Class, function, method, or alias.
    :type obj: type or function or alias

    :return: Origin class and arguments or (None, None).
    :rtype: tuple[type, tuple] or tuple[None, None]
    """
    if getattr(obj, "__args__", None) is not None and inspect.isclass(
        getattr(obj, "__origin__", None)
    ):
        return obj.__origin__, obj.__args__
    else:
        return None, None


def get_import_path(obj, force_ast=False, builtin_modules=None):
    # type: (Any, bool, Optional[Union[str, Iterable[str]]]) -> str
    """
    Get import path for object.

    :param obj: Class, function, method, or alias.
    :type obj: type or function or alias

    :param force_ast: Force use AST parser to get qualified name from code.
    :type force_ast: bool

    :param builtin_modules: Built-in module paths for looking up paths without a module.
    :type builtin_modules: str or tuple[str] or None

    :return: Import path.
    :rtype: str

    :raises TypeError: Provided obj type is invalid.
    :raises AttributeError: Could not access obj name and/or module.
    :raises ImportError: Import path is not consistent.
    """

    # Can't be None.
    if obj is None:
        error = "obj can't be None"
        raise TypeError(error)

    # Get generic origin, args, and suffix.
    generic_origin, generic_args = _get_alias_origin_and_args(obj)
    if generic_origin is not None:
        assert generic_args is not None
        generic_suffix = "".join(
            (
                "[",
                ", ".join(
                    get_import_path(
                        a, force_ast=force_ast, builtin_modules=builtin_modules
                    )
                    for a in generic_args
                ),
                "]",
            )
        )
    else:
        generic_suffix = ""

    # Get qualified name and module.
    try:
        if generic_origin is None:
            if not hasattr(obj, "__name__"):
                error = "can't get name for {}".format(obj)
                raise AttributeError(error)
            module = getattr(obj, "__module__", None)
            qual_name = get_qualified_name(
                obj, force_ast=force_ast, fallback=obj.__name__
            )
        else:
            module = getattr(generic_origin, "__module__", None)
            qual_name = get_qualified_name(
                generic_origin, force_ast=force_ast, fallback=generic_origin.__name__
            )
        if not module:
            error = "can't get module for {}".format(obj)
            raise AttributeError(error)
        if "<locals>" in qual_name:
            error = "local name {} is not importable".format(qual_name)
            raise AttributeError(error)
    except QualnameError:

        # Something went wrong getting the qualified name, print the traceback.
        print_exc()

        exc = AttributeError("couldn't get qualified name for {}".format(obj))
        raise_from(exc, None)
        raise exc

    # Join and verify import path.
    import_path = format_import_path(
        MODULE_SEPARATOR.join((module, qual_name)) + generic_suffix
    )
    try:
        imported_obj = import_from_path(import_path, builtin_modules=builtin_modules)
    except (ValueError, ImportError, AttributeError):

        # Something went wrong during import, print the traceback (will raise below).
        print_exc()
        imported_obj = None

    # Check if imported object is equal to the original object.
    # Don't use inequality due to a bug in Python 2's `typing.GenericMeta.__ne__`.
    if imported_obj == obj:
        return import_path

    else:

        # Not consistent (imported object is not equal, or something else went wrong).
        error = "import path {} is not consistent for {} (id:{}){}".format(
            repr(import_path),
            obj,
            id(obj),
            "; got {} (id: {}) when importing from it".format(
                imported_obj,
                id(imported_obj),
            )
            if imported_obj is not None
            else "; see traceback above",
        )
        raise ImportError(error)
