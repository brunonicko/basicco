from re import match as re_match
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, Optional

__all__ = ["privatize_name", "deprivatize_name"]


def privatize_name(cls_name, name):
    # type: (str, str) -> str
    """
    Privatize a member name if possible.

    :param cls_name: Owner class name.
    :type cls_name: str

    :param name: Name.
    :type name: str

    :return: Privatized name.
    :rtype: str
    """
    if name.startswith("__") and not name.endswith("__"):
        return "_{}{}".format(cls_name.lstrip("_"), name)
    return name


def deprivatize_name(name):
    # type: (str) -> Tuple[str, Optional[str]]
    """
    De-privatize a member name if possible.

    :param name: Name.
    :type name: str

    :return: Deprivatized name and owner class name (or None).
    :rtype: tuple[str, str or None]
    """
    matches = re_match(r"^_([^_]+)__[^_]+.*?(?<!__)$", name)
    if matches:
        cls_name = matches.groups()[0]
        return name[len(cls_name) + 1 :], cls_name
    return name, None
