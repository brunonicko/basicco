"""Utilities to retrieve the caller's module name."""

import inspect
from typing import Optional

__all__ = ["caller_module"]


def caller_module(frames: int = 0) -> Optional[str]:
    """
    Get caller module name if possible.

    :param frames: How many frames to go back.
    :return: Module name or None.
    """
    try:
        frame = inspect.stack()[2 + frames]
        module = inspect.getmodule(frame[0])
    except IndexError:
        return None
    else:
        if module is None:
            return None
        else:
            return module.__name__
