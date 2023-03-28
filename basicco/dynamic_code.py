"""Dynamic code generation."""

import linecache

from tippo import Any, Callable, Dict, List, Tuple, Union, cast

__all__ = ["compile_and_eval", "generate_unique_filename", "make_function"]


def compile_and_eval(script, globs=None, locs=None, filename=""):
    # type: (str, Union[Dict[str, Any], None], Union[Dict[str, Any], None], str) -> None
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
    # type: (str, Union[str, None], Union[str, None]) -> str
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


def make_function(
    name,  # type: str
    script,  # type: str
    globs=None,  # type: Union[Dict[str, Any], None]
    filename=None,  # type: Union[str, None]
    module=None,  # type: Union[str, None]
):
    # type: (...) -> Callable[..., Any]
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
    # FIXME: infinite looping here when dup function is generated
    if filename:
        count = 1
        base_filename = complete_filename = filename  # type: str
        while True:
            linecache_tuple = (
                len(script),
                None,
                script.splitlines(True),
                complete_filename,
            )  # type: Tuple[int, Union[float, None], List[str], str]
            old_val = linecache.cache.setdefault(complete_filename, linecache_tuple)
            if old_val == linecache_tuple:
                break
            else:
                complete_filename = "{}-{}>".format(base_filename[:-1], count)
                count += 1
    else:
        complete_filename = ""

    # Compile and evaluate.
    locs = {}  # type: Dict[str, Any]
    compile_and_eval(script, globs, locs, complete_filename)
    func = locs[name]

    # Set module name.
    if module is not None:
        object.__setattr__(func, "__module__", module)

    return cast("Callable[..., Any]", func)
