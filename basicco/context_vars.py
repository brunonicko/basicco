"""
Backport of `contextvars`.
Based on `MagicStack/contextvars <https://github.com/MagicStack/contextvars>`_.
"""

__all__ = ["ContextVar", "Context", "Token", "copy_context"]


try:
    from contextvars import Context, ContextVar, Token, copy_context  # noqa

except ImportError:
    import enum
    import threading

    import six
    from tippo import (
        Any,
        Callable,
        Dict,
        Generic,
        GenericMeta,
        Iterator,
        Mapping,
        Tuple,
        Type,
        TypeVar,
        Union,
        cast,
        overload,
    )

    class _NoDefaultType(enum.Enum):
        NO_DEFAULT = "NO_DEFAULT"

    _NO_DEFAULT = _NoDefaultType.NO_DEFAULT
    _MODULE = __name__

    _T = TypeVar("_T")
    _RT = TypeVar("_RT")

    class _ContextVarMeta(GenericMeta):
        @staticmethod
        def __new__(
            mcs,  # type: Type[_CVM]
            name,  # type: str
            bases,  # type: Tuple[Type[Any], ...]
            dct,  # type: Dict[str, Any]
            **kwargs  # type: Any
        ):
            # type: (...) -> _CVM
            cls = super(_ContextVarMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            if cls.__module__ != _MODULE or cls.__name__ != "_ContextVar":
                raise TypeError("type '_ContextVar' is not an acceptable base type")
            return cls

    _CVM = TypeVar("_CVM", bound=_ContextVarMeta)

    class _ContextVar(six.with_metaclass(_ContextVarMeta, Generic[_T])):
        __slots__ = ("__weakref__", "_name", "_default")

        def __init__(self, name, default=_NO_DEFAULT):
            # type: (str, Union[_T, _NoDefaultType]) -> None
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
            # type: (Union[_T, _NoDefaultType]) -> _T
            pass

        @overload
        def get(self, default=_NO_DEFAULT):
            # type: (Any) -> Any
            pass

        def get(self, default=_NO_DEFAULT):
            # type: (Any) -> Any
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
            # type: (_T) -> _Token[_T]
            ctx = _get_context()
            data = ctx._data  # noqa
            try:
                old_value = data[self]
            except KeyError:
                old_value = _Token.MISSING

            updated_data = data.copy()
            updated_data[self] = value
            ctx._data = updated_data
            return _Token(ctx, self, old_value)

        def reset(self, token):
            # type: (_Token[_T]) -> None
            if token._used:
                raise RuntimeError("_Token has already been used once")

            if token._var is not self:  # noqa
                raise ValueError("_Token was created by a different _ContextVar")

            if token._context is not _get_context():  # noqa
                raise ValueError("_Token was created in a different Context")

            ctx = token._context
            updated_data = ctx._data.copy()
            if token._old_value is _Token.MISSING:
                del updated_data[token._var]
            else:
                updated_data[token._var] = token._old_value
            ctx._data = updated_data

            token._used = True

        def __repr__(self):
            # type: () -> str
            r = "<ContextVar name={!r}".format(self.name)
            if self._default is not _NO_DEFAULT:
                r += " default={!r}".format(self._default)
            return r + " at {:0x}>".format(id(self))

    class _ContextMeta(GenericMeta):
        @staticmethod
        def __new__(
            mcs,  # type: Type[_CM]
            name,  # type: str
            bases,  # type: Tuple[Type[Any], ...]
            dct,  # type: Dict[str, Any]
            **kwargs  # type: Any
        ):
            # type: (...) -> _CM
            cls = super(_ContextMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            if cls.__module__ != _MODULE or cls.__name__ != "_Context":
                raise TypeError("type 'Context' is not an acceptable base type")
            return cls

    _CM = TypeVar("_CM", bound=_ContextMeta)

    class _Context(  # type: ignore
        six.with_metaclass(_ContextMeta, Mapping[_ContextVar[Any], Any])
    ):
        __slots__ = ("_data", "_prev_context")

        def __init__(self):
            # type: () -> None
            self._data = {}  # type: Dict[_ContextVar[Any], Any]
            self._prev_context = None  # type: Union[_Context, None]

        def run(self, func, *args, **kwargs):
            # type: (Callable[..., _RT], *Any, **Any) -> _RT
            if self._prev_context is not None:
                raise RuntimeError(
                    "cannot enter context: {} is already entered".format(self)
                )

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
            # type: (_ContextVar[_T]) -> _T
            if not isinstance(var, _ContextVar):
                raise TypeError("a _ContextVar key was expected, got {!r}".format(var))
            return cast(_T, self._data[var])

        def __contains__(self, var):
            # type: (Any) -> bool
            if not isinstance(var, _ContextVar):
                raise TypeError("a _ContextVar key was expected, got {!r}".format(var))
            return var in self._data

        def __len__(self):
            # type: () -> int
            return len(self._data)

        def __iter__(self):
            # type: () -> Iterator[_ContextVar[Any]]
            for var in self._data:
                yield var

    class _TokenMeta(GenericMeta):
        @staticmethod
        def __new__(
            mcs,  # type: Type[_TM]
            name,  # type: str
            bases,  # type: Tuple[Type[Any], ...]
            dct,  # type: Dict[str, Any]
            **kwargs  # type: Any
        ):
            # type: (...) -> _TM
            cls = super(_TokenMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            if cls.__module__ != _MODULE or cls.__name__ != "_Token":
                raise TypeError("type '_Token' is not an acceptable base type")
            return cls

    _TM = TypeVar("_TM", bound=_TokenMeta)

    class _Token(six.with_metaclass(_TokenMeta, Generic[_T])):
        __slots__ = ("__weakref__", "_context", "_var", "_old_value", "_used")

        MISSING = object()

        def __init__(self, context, var, old_value):
            # type: (_Context, _ContextVar[_T], _T) -> None
            self._context = context
            self._var = var
            self._old_value = old_value
            self._used = False

        @property
        def var(self):
            # type: () -> _ContextVar[_T]
            return self._var

        @property
        def old_value(self):
            # type: () -> _T
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
