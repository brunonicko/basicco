import functools
import sys

import pytest  # noqa

from basicco.context_vars import Context, ContextVar, Token, copy_context

_var = ContextVar("_var")  # type: ContextVar[str]
_default_var = ContextVar("_default_var", default="default")  # type: ContextVar[str]


def _isolated_context(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = Context()
        return ctx.run(func, *args, **kwargs)

    return wrapper


def test_compat():
    if sys.version_info[0:2] >= (3, 7):
        import contextvars  # noqa

        assert ContextVar is contextvars.ContextVar
        assert Context is contextvars.Context
        assert Token is contextvars.Token
        assert copy_context is contextvars.copy_context
    else:
        with pytest.raises(ImportError):
            import contextvars  # noqa


def test_var():
    with pytest.raises(LookupError):
        _var.get()
    assert _var.get(None) is None

    token = _var.set("foo")
    assert _var.get() == "foo"
    _var.reset(token)

    with pytest.raises(LookupError):
        _var.get()  # type: ignore
    assert _var.get(None) is None


def test_default_var():
    assert _default_var.get() == "default"
    assert _var.get(None) is None

    token = _default_var.set("foo")
    assert _default_var.get() == "foo"
    _default_var.reset(token)

    assert _default_var.get() == "default"
    assert _var.get(None) is None


def test_context_var_new():
    with pytest.raises(TypeError):
        ContextVar()  # type: ignore

    exp = "must be a str"
    with pytest.raises(TypeError) as exc:
        ContextVar(1)  # type: ignore
    assert exp in str(exc)

    c = ContextVar("a")
    assert hash(c) != hash("a")


@_isolated_context
def test_context_var_repr_1():
    c = ContextVar("a")
    assert "a" in repr(c)

    c = ContextVar("a", default=123)
    assert "123" in repr(c)

    lst = []
    c = ContextVar("a", default=lst)
    lst.append(c)
    assert "..." in repr(c)
    assert "..." in repr(lst)

    t = c.set(1)
    assert repr(c) in repr(t)

    assert " used " not in repr(t)
    c.reset(t)
    assert " used " in repr(t)


def test_context_subclassing_1():
    exp = "not an acceptable base type"
    with pytest.raises(TypeError) as exc:

        class MyContextVar(ContextVar):  # type: ignore
            pass

        assert not MyContextVar
    assert exp in str(exc)

    exp = "not an acceptable base type"
    with pytest.raises(TypeError) as exc:

        class MyContext(Context):  # type: ignore
            pass

        assert not MyContext
    assert exp in str(exc)

    exp = "not an acceptable base type"
    with pytest.raises(TypeError) as exc:

        class MyToken(Token):  # type: ignore
            pass

        assert not MyToken
    assert exp in str(exc)


def test_context_new_1():
    with pytest.raises(TypeError):
        Context(1)  # type: ignore
    with pytest.raises(TypeError):
        Context(1, a=1)  # type: ignore
    with pytest.raises(TypeError):
        Context(a=1)  # type: ignore
    Context(**{})  # type: ignore


def test_context_type_errors_1():
    ctx = Context()

    exp = "ContextVar key was expected"
    with pytest.raises(TypeError) as exc:
        _ = ctx[1]  # type: ignore
    assert exp in str(exc)

    exp = "ContextVar key was expected"
    with pytest.raises(TypeError) as exc:
        _ = 1 in ctx
    assert exp in str(exc)

    exp = "ContextVar key was expected"
    with pytest.raises(TypeError) as exc:
        _ = ctx.get(1)  # type: ignore
    assert exp in str(exc)


def test_context_get_context_1():
    ctx = copy_context()
    assert isinstance(ctx, Context)


def test_context_run_1():
    ctx = Context()

    with pytest.raises(TypeError):
        ctx.run()  # type: ignore


def test_context_run_2():
    ctx = Context()

    def func(*args, **kwargs):
        kwargs["spam"] = "foo"
        args += ("bar",)
        return args, kwargs

    for f in (func, functools.partial(func)):
        assert ctx.run(f) == (("bar",), {"spam": "foo"})
        assert ctx.run(f, 1) == ((1, "bar"), {"spam": "foo"})

        assert ctx.run(f, a=2) == (("bar",), {"a": 2, "spam": "foo"})

        assert ctx.run(f, 11, a=2) == ((11, "bar"), {"a": 2, "spam": "foo"})

        a = {}
        assert ctx.run(f, 11, **a) == ((11, "bar"), {"spam": "foo"})
        assert a == {}


def test_context_run_3():
    ctx = Context()

    def func(*args, **kwargs):  # noqa
        _ = 1 / 0

    with pytest.raises(ZeroDivisionError):
        ctx.run(func)

    with pytest.raises(ZeroDivisionError):
        ctx.run(func, 1, 2)

    with pytest.raises(ZeroDivisionError):
        ctx.run(func, 1, 2, a=123)


@_isolated_context
def test_context_run_4():
    ctx1 = Context()
    ctx2 = Context()
    var = ContextVar("var")

    def func2():
        assert var.get(None) is None

    def func1():
        assert var.get(None) is None
        var.set("spam")
        ctx2.run(func2)
        assert var.get(None) == "spam"

        cur = copy_context()
        assert len(cur) == 1
        assert cur[var] == "spam"
        return cur

    returned_ctx = ctx1.run(func1)
    assert ctx1 == returned_ctx
    assert returned_ctx[var] == "spam"
    assert var in returned_ctx


def test_context_run_5():
    ctx = Context()
    var = ContextVar("var")

    def func():
        assert var.get(None) is None
        var.set("spam")
        _ = 1 / 0

    with pytest.raises(ZeroDivisionError):
        ctx.run(func)

    assert var.get(None) is None


def test_context_run_6():
    ctx = Context()
    c = ContextVar("a", default=0)

    def fun():
        assert c.get() == 0
        assert ctx.get(c) is None

        c.set(42)
        assert c.get() == 42
        assert ctx.get(c) == 42

    ctx.run(fun)


def test_context_run_7():
    ctx = Context()

    def fun():
        exp = "is already entered"
        with pytest.raises(RuntimeError) as exc:
            ctx.run(fun)
        assert exp in str(exc)

    ctx.run(fun)


@_isolated_context
def test_context_getset_1():
    c = ContextVar("c")
    with pytest.raises(LookupError):
        c.get()

    assert c.get(None) is None

    t0 = c.set(42)
    assert c.get() == 42
    assert c.get(None) == 42
    assert t0.old_value is t0.MISSING
    assert t0.old_value is Token.MISSING
    assert t0.var is c

    t = c.set("spam")
    assert c.get() == "spam"
    assert c.get(None) == "spam"
    assert t.old_value == 42
    c.reset(t)

    assert c.get() == 42
    assert c.get(None) == 42

    c.set("spam2")
    exp = "has already been used"
    with pytest.raises(RuntimeError) as exc:
        c.reset(t)
    assert exp in str(exc)

    assert c.get() == "spam2"

    ctx1 = copy_context()
    assert c in ctx1

    c.reset(t0)
    exp = "has already been used"
    with pytest.raises(RuntimeError) as exc:
        c.reset(t0)
    assert exp in str(exc)

    assert c.get(None) is None

    assert c in ctx1
    assert ctx1[c] == "spam2"
    assert ctx1.get(c, "aa") == "spam2"
    assert len(ctx1) == 1
    assert list(ctx1.items()) == [(c, "spam2")]
    assert list(ctx1.values()) == ["spam2"]
    assert list(ctx1.keys()) == [c]
    assert list(ctx1) == [c]

    ctx2 = copy_context()
    assert c not in ctx2
    with pytest.raises(KeyError):
        _ = ctx2[c]
    assert ctx2.get(c, "aa") == "aa"
    assert len(ctx2) == 0
    assert list(ctx2) == []


@_isolated_context
def test_context_getset_2():
    v1 = ContextVar("v1")
    v2 = ContextVar("v2")

    t1 = v1.set(42)
    exp = "by a different"
    with pytest.raises(ValueError) as exc:
        v2.reset(t1)
    assert exp in str(exc)


@_isolated_context
def test_context_getset_3():
    c = ContextVar("c", default=42)
    ctx = Context()

    def fun():
        assert c.get() == 42
        with pytest.raises(KeyError):
            _ = ctx[c]
        assert ctx.get(c) is None
        assert ctx.get(c, "spam") == "spam"
        assert c not in ctx
        assert list(ctx.keys()) == []

        t = c.set(1)
        assert list(ctx.keys()) == [c]
        assert ctx[c], 1

        c.reset(t)
        assert list(ctx.keys()) == []
        with pytest.raises(KeyError):
            _ = ctx[c]

    ctx.run(fun)


@_isolated_context
def test_context_getset_4():
    c = ContextVar("c", default=42)
    ctx = Context()

    tok = ctx.run(c.set, 1)

    exp = "different Context"
    with pytest.raises(ValueError) as exc:
        c.reset(tok)
    assert exp in str(exc)


@_isolated_context
def test_context_getset_5():
    c = ContextVar("c", default=42)  # type: ContextVar[int | list]
    c.set([])

    def fun():
        c.set([])
        c.get().append(42)
        assert c.get() == [42]

    copy_context().run(fun)
    assert c.get() == []


def test_context_copy_1():
    ctx1 = Context()
    c = ContextVar("c", default=42)

    def ctx1_fun():
        c.set(10)

        ctx2 = ctx1.copy()
        assert ctx2[c] == 10

        c.set(20)
        assert ctx1[c] == 20
        assert ctx2[c] == 10

        ctx2.run(ctx2_fun)
        assert ctx1[c] == 20
        assert ctx2[c] == 30

    def ctx2_fun():
        assert c.get() == 10
        c.set(30)
        assert c.get() == 30

    ctx1.run(ctx1_fun)


if __name__ == "__main__":
    pytest.main()
