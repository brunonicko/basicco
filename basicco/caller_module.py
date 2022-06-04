"""Retrieve the caller's module name."""

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
            try:
                return frame[0].f_globals["__name__"]
            except (IndexError, KeyError):
                return None
        else:
            return module.__name__
