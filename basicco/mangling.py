"""Name mangling utilities."""

import re

__all__ = ["mangle", "unmangle", "extract"]


def mangle(name, cls_name):
    # type: (str, str) -> str
    """
    Mangle a name with a class name if applicable.

    :param name: Name.
    :param cls_name: Class name.
    :return: Mangled name.
    """
    if name.startswith("__") and not name.endswith("__"):
        return "_{}{}".format(cls_name.lstrip("_"), name)
    return name


def unmangle(name, cls_name):
    # type: (str, str) -> str
    """
    Unmangle a mangled name with a class name if applicable.

    :param name: Name.
    :param cls_name: Class name.
    :return: Unmangled name.
    """
    prefix = "_{}".format(cls_name.lstrip("_"))
    if name.startswith("{}__".format(prefix)):
        unmangled_name = name[len(prefix) :]
        if unmangled_name.startswith("__") and unmangled_name.endswith("__"):
            return name
        return name[len(prefix) :]
    return name


def extract(name):
    # type: (str) -> tuple[str, str | None]
    """
    Extract name and class name from mangled name if applicable.

    :param name: Mangled name.
    :return: Unmangled name and class name (or None).
    """
    matches = re.match(r"^_([^_]+)__[^_]+.*?(?<!__)$", name)
    if matches:
        cls_name = matches.groups()[0]
        return name[len(cls_name) + 1 :], cls_name
    return name, None
