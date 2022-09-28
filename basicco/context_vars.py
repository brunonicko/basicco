"""
Backport of `contextvars` for Python 2.7.
Based on `MagicStack/contextvars <https://github.com/MagicStack/contextvars>`_.
"""

__all__ = ["ContextVar", "Context", "Token", "copy_context"]


try:
    from contextvars import Context, ContextVar, Token, copy_context  # noqa

except ImportError:
    import enum
    import threading

    import pyrsistent
    import six
    from pyrsistent.typing import PMap
    from tippo import (
        Any,
        Callable,
        Generic,
        GenericMeta,
        Iterator,
        Mapping,
        TypeVar,
        overload,
    )

    class _NoDefaultType(enum.Enum):
        NO_DEFAULT = "NO_DEFAULT"

    _NO_DEFAULT = _NoDefaultType.NO_DEFAULT
    _MODULE = __name__

    T = TypeVar("T")
    RT = TypeVar("RT")

    class _ContextVarMeta(GenericMeta):
        def __new__(mcs, names, bases, dct, **kwargs):
            cls = super(_ContextVarMeta, mcs).__new__(mcs, names, bases, dct, **kwargs)
            if cls.__module__ != _MODULE or cls.__name__ != "_ContextVar":
                raise TypeError("type '_ContextVar' is not an acceptable base type")
            return cls

    class _ContextVar(six.with_metaclass(_ContextVarMeta, Generic[T])):
        __slots__ = ("__weakref__", "_name", "_default")

        def __init__(self, name, default=_NO_DEFAULT):
            # type: (str, T | _NoDefaultType) -> None
            if not isinstance(name, str):
                raise TypeError("context variable name must be a str")
            self._name = name
            self._default = default

        @property
        def name(self):
            # type: () -> str
            return self._name

        @overload
        def get(self, default=_NO_DEFAULT):
            # type: (T | _NoDefaultType) -> T
            pass

        @overload
        def get(self, default=_NO_DEFAULT):
            # type: (Any) -> Any
            pass

        def get(self, default=_NO_DEFAULT):
            ctx = _get_context()
            try:
                return ctx[self]
            except KeyError:
                pass

            if default is not _NO_DEFAULT:
                return default

            if self._default is not _NO_DEFAULT:
                return self._default

            raise LookupError()

        def set(self, value):
            # type: (T) -> _Token[T]
            ctx = _get_context()
            data = ctx._data  # noqa
            try:
                old_value = data[self]
            except KeyError:
                old_value = _Token.MISSING

            updated_data = data.set(self, value)
            ctx._data = updated_data
            return _Token(ctx, self, old_value)

        def reset(self, token):
            # type: (_Token[T]) -> None
            if token._used:
                raise RuntimeError("_Token has already been used once")

            if token._var is not self:  # noqa
                raise ValueError("_Token was created by a different _ContextVar")

            if token._context is not _get_context():  # noqa
                raise ValueError("_Token was created in a different Context")

            ctx = token._context  # noqa
            if token._old_value is _Token.MISSING:  # noqa
                ctx._data = ctx._data.remove(token._var)  # noqa
            else:
                ctx._data = ctx._data.set(token._var, token._old_value)  # noqa

            token._used = True

        def __repr__(self):
            # type: () -> str
            r = "<ContextVar name={!r}".format(self.name)
            if self._default is not _NO_DEFAULT:
                r += " default={!r}".format(self._default)
            return r + " at {:0x}>".format(id(self))

    class _ContextMeta(GenericMeta):
        def __new__(mcs, names, bases, dct, **kwargs):
            cls = super(_ContextMeta, mcs).__new__(mcs, names, bases, dct, **kwargs)
            if cls.__module__ != _MODULE or cls.__name__ != "_Context":
                raise TypeError("type 'Context' is not an acceptable base type")
            return cls

    class _Context(six.with_metaclass(_ContextMeta, Mapping)):  # type: ignore
        __slots__ = ("_data", "_prev_context")

        def __init__(self):
            # type: () -> None
            self._data = pyrsistent.pmap()  # type: PMap[_ContextVar, Any]
            self._prev_context = None  # type: _Context | None

        def run(self, func, *args, **kwargs):
            # type: (Callable[..., RT], *Any, **Any) -> RT
            if self._prev_context is not None:
                raise RuntimeError("cannot enter context: {} is already entered".format(self))

            self._prev_context = _get_context()
            try:
                _set_context(self)
                return func(*args, **kwargs)
            finally:
                _set_context(self._prev_context)
                self._prev_context = None

        def copy(self):
            # type: () -> _Context
            new = _Context()
            new._data = self._data
            return new

        def __getitem__(self, var):
            # type: (_ContextVar[T]) -> T
            if not isinstance(var, _ContextVar):
                raise TypeError("a _ContextVar key was expected, got {!r}".format(var))
            return self._data[var]

        def __contains__(self, var):
            # type: (Any) -> bool
            if not isinstance(var, _ContextVar):
                raise TypeError("a _ContextVar key was expected, got {!r}".format(var))
            return var in self._data

        def __len__(self):
            # type: () -> int
            return len(self._data)

        def __iter__(self):
            # type: () -> Iterator[_ContextVar]
            for var in self._data:
                yield var

    class _TokenMeta(GenericMeta):
        def __new__(mcs, names, bases, dct, **kwargs):
            cls = super(_TokenMeta, mcs).__new__(mcs, names, bases, dct, **kwargs)
            if cls.__module__ != _MODULE or cls.__name__ != "_Token":
                raise TypeError("type '_Token' is not an acceptable base type")
            return cls

    class _Token(six.with_metaclass(_TokenMeta, Generic[T])):  # type: ignore
        __slots__ = ("__weakref__", "_context", "_var", "_old_value", "_used")

        MISSING = object()

        def __init__(self, context, var, old_value):
            # type: (_Context, _ContextVar[T], T) -> None
            self._context = context
            self._var = var
            self._old_value = old_value
            self._used = False

        @property
        def var(self):
            # type: () -> _ContextVar[T]
            return self._var

        @property
        def old_value(self):
            # type: () -> T
            return self._old_value

        def __repr__(self):
            # type: () -> str
            r = "<Token "
            if self._used:
                r += " used"
            r += " var={!r} at {:0x}>".format(self._var, id(self))
            return r

    def _copy_context():
        # type: () -> _Context
        return _get_context().copy()

    def _get_context():
        # type: () -> _Context
        ctx = getattr(_state, "context", None)
        if ctx is None:
            ctx = _Context()
            _state.context = ctx
        return ctx

    def _set_context(ctx):
        # type: (_Context) -> None
        _state.context = ctx

    _state = threading.local()

    type.__setattr__(_ContextVar, "__name__", "ContextVar")
    type.__setattr__(_ContextVar, "__qualname__", "ContextVar")
    globals()["ContextVar"] = _ContextVar

    type.__setattr__(_Context, "__name__", "Context")
    type.__setattr__(_Context, "__qualname__", "Context")
    globals()["Context"] = _Context

    type.__setattr__(_Token, "__name__", "Token")
    type.__setattr__(_Token, "__qualname__", "Token")
    globals()["Token"] = _Token

    object.__setattr__(_copy_context, "__name__", "copy_context")
    object.__setattr__(_copy_context, "__qualname__", "copy_context")
    globals()["copy_context"] = _copy_context
