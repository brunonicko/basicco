"""Backport of `contextvars` for Python 2.7. Based on `MagicStack/contextvars`."""

__all__ = ["ContextVar", "Context", "Token", "copy_context"]


try:
    import contextvars  # noqa

    globals()["ContextVar"] = contextvars.ContextVar
    globals()["Context"] = contextvars.Context
    globals()["Token"] = contextvars.Token
    globals()["copy_context"] = contextvars.copy_context

except ImportError:
    import threading

    import six
    import enum
    import pyrsistent
    from pyrsistent.typing import PMap
    from tippo import Any, Callable, GenericMeta, Generic, Mapping, TypeVar, Iterator, overload

    class _NoDefaultType(enum.Enum):
        NO_DEFAULT = "NO_DEFAULT"

    NO_DEFAULT = _NoDefaultType.NO_DEFAULT
    _MODULE = __name__

    T = TypeVar("T")
    RT = TypeVar("RT")

    class ContextVarMeta(GenericMeta):
        def __new__(mcs, names, bases, dct, **kwargs):
            cls = super(ContextVarMeta, mcs).__new__(mcs, names, bases, dct, **kwargs)
            if cls.__module__ != _MODULE or cls.__name__ != "ContextVar":
                raise TypeError("type 'ContextVar' is not an acceptable base type")
            return cls

    class ContextVar(six.with_metaclass(ContextVarMeta, Generic[T])):
        __slots__ = ("__weakref__", "_name", "_default")

        def __init__(self, name, default=NO_DEFAULT):
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
        def get(self, default=NO_DEFAULT):
            # type: (T | _NoDefaultType) -> T
            pass

        @overload
        def get(self, default=NO_DEFAULT):
            # type: (Any) -> Any
            pass

        def get(self, default=NO_DEFAULT):
            ctx = _get_context()
            try:
                return ctx[self]
            except KeyError:
                pass

            if default is not NO_DEFAULT:
                return default

            if self._default is not NO_DEFAULT:
                return self._default

            raise LookupError

        def set(self, value):
            # type: (T) -> Token[T]
            ctx = _get_context()
            data = ctx._data  # noqa
            try:
                old_value = data[self]
            except KeyError:
                old_value = Token.MISSING

            updated_data = data.set(self, value)
            ctx._data = updated_data
            return Token(ctx, self, old_value)

        def reset(self, token):
            # type: (Token[T]) -> None
            if token._used:
                raise RuntimeError("Token has already been used once")

            if token._var is not self:  # noqa
                raise ValueError("Token was created by a different ContextVar")

            if token._context is not _get_context():  # noqa
                raise ValueError("Token was created in a different Context")

            ctx = token._context  # noqa
            if token._old_value is Token.MISSING:  # noqa
                ctx._data = ctx._data.remove(token._var)  # noqa
            else:
                ctx._data = ctx._data.set(token._var, token._old_value)  # noqa

            token._used = True

        def __repr__(self):
            # type: () -> str
            r = "<ContextVar name={!r}".format(self.name)
            if self._default is not NO_DEFAULT:
                r += " default={!r}".format(self._default)
            return r + " at {:0x}>".format(id(self))

    class ContextMeta(GenericMeta):
        def __new__(mcs, names, bases, dct, **kwargs):
            cls = super(ContextMeta, mcs).__new__(mcs, names, bases, dct, **kwargs)
            if cls.__module__ != _MODULE or cls.__name__ != "Context":
                raise TypeError("type 'Context' is not an acceptable base type")
            return cls

    class Context(six.with_metaclass(ContextMeta, Mapping)):  # type: ignore
        __slots__ = ("_data", "_prev_context")

        def __init__(self):
            # type: () -> None
            self._data = pyrsistent.pmap()  # type: PMap[ContextVar, Any]
            self._prev_context = None  # type: Context | None

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
            # type: () -> Context
            new = Context()
            new._data = self._data
            return new

        def __getitem__(self, var):
            # type: (ContextVar[T]) -> T
            if not isinstance(var, ContextVar):
                raise TypeError("a ContextVar key was expected, got {!r}".format(var))
            return self._data[var]

        def __contains__(self, var):
            # type: (Any) -> bool
            if not isinstance(var, ContextVar):
                raise TypeError("a ContextVar key was expected, got {!r}".format(var))
            return var in self._data

        def __len__(self):
            # type: () -> int
            return len(self._data)

        def __iter__(self):
            # type: () -> Iterator[ContextVar]
            for var in self._data:
                yield var

    class TokenMeta(GenericMeta):
        def __new__(mcs, names, bases, dct, **kwargs):
            cls = super(TokenMeta, mcs).__new__(mcs, names, bases, dct, **kwargs)
            if cls.__module__ != _MODULE or cls.__name__ != "Token":
                raise TypeError("type 'Token' is not an acceptable base type")
            return cls

    class Token(six.with_metaclass(TokenMeta, Generic[T])):  # type: ignore
        __slots__ = ("__weakref__", "_context", "_var", "_old_value", "_used")

        MISSING = object()

        def __init__(self, context, var, old_value):
            # type: (Context, ContextVar[T], T) -> None
            self._context = context
            self._var = var
            self._old_value = old_value
            self._used = False

        @property
        def var(self):
            # type: () -> ContextVar[T]
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

    def copy_context():
        # type: () -> Context
        return _get_context().copy()

    def _get_context():
        # type: () -> Context
        ctx = getattr(_state, "context", None)
        if ctx is None:
            ctx = Context()
            _state.context = ctx
        return ctx

    def _set_context(ctx):
        # type: (Context) -> None
        _state.context = ctx

    _state = threading.local()
