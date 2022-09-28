"""Dynamic code generation."""

import linecache

from tippo import Any, Callable

__all__ = ["compile_and_eval", "generate_unique_filename", "make_function"]


def compile_and_eval(script, globs=None, locs=None, filename=""):
    # type: (str, dict[str, Any], dict[str, Any] | None, str) -> None
    """
    Evaluate the script with the given globals and locals.

    :param script: Script.
    :param globs: Globals.
    :param locs: Locals.
    :param filename: Filename.
    """
    bytecode = compile(script, filename, "exec")
    eval(bytecode, globs, locs)


def generate_unique_filename(obj_name, module=None, owner_name=None):
    # type: (str, str | None, str | None) -> str
    """
    Create a unique 'filename' suitable for a generated object.

    :param obj_name: Object name.
    :param module: Module name.
    :param owner_name: Name of the class that will own the method.
    :return: Filename.
    """
    if owner_name is not None:
        if module is None:
            error = "specified 'owner_name' but no 'module'"
            raise ValueError(error)
        return "<generated {}.{}.{}>".format(module, owner_name, obj_name)
    elif module is not None:
        return "<generated {}.{}>".format(module, obj_name)
    else:
        return "<generated {}>".format(obj_name)


def make_function(name, script, globs=None, filename=None, module=None):
    # type: (str, str, dict[str, Any], str | None, str | None) -> Callable
    """
    Create a function with the given script.

    :param name: Function name.
    :param script: Script.
    :param filename: Filename.
    :param globs: Globals.
    :param module: Module name.
    :return: Function object.
    """

    # Add a fake linecache entry for debuggers.
    if filename:
        count = 1
        base_filename = complete_filename = filename  # type: str
        while True:
            linecache_tuple = (
                len(script),
                None,
                script.splitlines(True),
                complete_filename,
            )  # type: tuple[int, float | None, list[str], str]
            old_val = linecache.cache.setdefault(filename, linecache_tuple)
            if old_val == linecache_tuple:
                break
            else:
                complete_filename = "{}-{}>".format(base_filename[:-1], count)
                count += 1
    else:
        complete_filename = ""

    # Compile and evaluate.
    locs = {}  # type: dict[str, Any]
    compile_and_eval(script, globs, locs, complete_filename)
    func = locs[name]

    # Set module name.
    if module is not None:
        object.__setattr__(func, "__module__", module)

    return func
