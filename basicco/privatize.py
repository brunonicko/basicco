"""Functions to privatize/deprivatize member names."""

import re
from typing import Tuple, Optional

__all__ = ["privatize", "deprivatize"]


def privatize(name: str, cls_name: str) -> str:
    """
    Privatize a member name if possible.

    :param name: Name.
    :param cls_name: Owner class name.
    :return: Privatized name.
    """
    if name.startswith("__") and not name.endswith("__"):
        return "_{}{}".format(cls_name.lstrip("_"), name)
    return name


def deprivatize(name: str) -> Tuple[str, Optional[str]]:
    """
    De-privatize a member name if possible.

    :param name: Name.
    :return: Deprivatized name and owner class name (or None).
    """
    matches = re.match(r"^_([^_]+)__[^_]+.*?(?<!__)$", name)
    if matches:
        cls_name = matches.groups()[0]
        return name[len(cls_name) + 1 :], cls_name
    return name, None
