"""Rough implementation of ContextVar for Python 2.7 that works with threads."""

from __future__ import absolute_import, division, print_function

import uuid

from tippo import TypeVar, Generic

__all__ = ["ContextVar", "Token"]


_T = TypeVar("_T")


try:
    from contextvars import Token, ContextVar  # noqa
except ImportError:
    from threading import local

    _local = local()
    MISSING = object()

    class Token(Generic[_T]):  # type: ignore
        __slots__ = ("__var", "__old_value")

        MISSING = MISSING

        def __init__(self, var, old_value):
            # type: (ContextVar, _T) -> None
            self.__var = var
            self.__old_value = old_value

        @property
        def var(self):
            # type: () -> ContextVar[_T]
            return self.__var

        @property
        def old_value(self):
            # type: () -> _T
            return self.__old_value

    class ContextVar(Generic[_T]):  # type: ignore
        __slots__ = ("__uuid", "__name", "__default")

        def __init__(self, name, default=MISSING):
            self.__uuid = "_{}".format(str(uuid.uuid4()).replace("-", "_"))
            self.__name = name
            self.__default = default

        def get(self, default=MISSING):
            # type: (...) -> _T
            try:
                return getattr(_local, self.__uuid)
            except AttributeError:
                if default is not MISSING:
                    return default
                if self.__default is not MISSING:
                    return self.__default
            error = "no value set in current context for context variable {!r}".format(self.name)
            raise LookupError(error)

        def set(self, value):
            # type: (_T) -> Token[_T]
            try:
                old_value = getattr(_local, self.__uuid)
            except AttributeError:
                old_value = MISSING
            setattr(_local, self.__uuid, value)
            return Token(self, old_value)  # type: ignore

        def reset(self, token):
            # type: (Token) -> None
            if token.old_value is MISSING:
                delattr(_local, self.__uuid)
            else:
                setattr(_local, self.__uuid, token.old_value)

        @property
        def name(self):
            # type: () -> str
            return self.__name
