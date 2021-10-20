"""Python-2 compatile way of finding the qualified name of a class/method."""

import ast
import inspect
from typing import TYPE_CHECKING

from six import raise_from

if TYPE_CHECKING:
    from typing import Callable, Dict, Optional

__all__ = ["qualname", "QualnameError", "QualnameMeta"]

_QUALNAME_ATTR = "__qualname__"
_QUALNAME_CACHE_ATTR = "__qualname"
_HAS_NATIVE_QUALNAME = hasattr(type, _QUALNAME_ATTR)

_cache = {}  # type: Dict[str, Dict[int, str]]


class _Visitor(ast.NodeVisitor):
    def __init__(self):
        self.stack = []
        self.qualnames = {}

    def store_qualname(self, lineno):
        qn = ".".join(n for n in self.stack)
        self.qualnames[lineno] = qn

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.store_qualname(node.lineno)
        self.stack.append("<locals>")
        self.generic_visit(node)
        self.stack.pop()
        self.stack.pop()

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        self.store_qualname(node.lineno)
        self.generic_visit(node)
        self.stack.pop()


class QualnameError(Exception):
    pass


def qualname(obj, fallback=None, force_ast=False):
    # type: (Callable, Optional[str], bool) -> str
    """
    Try to find out the qualified name for a class or function.
    This function uses ast parsing in Python 2 to try to replicate the qualified name
    functionality available in Python 3.3+.

    :param obj: Function or class.
    :type obj: function or type

    :param fallback: Value to return if couldn't get qualified name. Will error if None.
    :type fallback: None or str

    :param force_ast: Force use AST parser to get qualified name from code.
    :type force_ast: bool

    :return: Qualified name (or None if not available).
    :rtype: str

    :raises TypeError: Provided object is not a function or a class.
    :raises QualnameError: Could not get qualified name from AST parsing.
    """

    # Not available for non-callables.
    if not callable(obj) or not hasattr(obj, "__name__"):
        error = "can't determine qualified name for instances of {}".format(
            repr(type(obj).__name__)
        )
        raise TypeError(error)

    # Native qualified name or manually defined.
    if not force_ast:
        try:
            return getattr(obj, _QUALNAME_ATTR)
        except QualnameError:
            if fallback is not None:
                return fallback
            else:
                raise
        except AttributeError:
            pass

    # Get source file name.
    try:
        filename = inspect.getsourcefile(obj)
        if filename is None:
            raise TypeError()
    except TypeError:
        if fallback is None:
            error = "couldn't find source code filename for {}".format(
                repr(obj.__name__)
            )
            exc = QualnameError(error)
            raise_from(exc, None)
            raise exc
        else:
            return fallback

    # Get line number.
    if inspect.isclass(obj):
        try:
            _, lineno = inspect.getsourcelines(obj)
        except (OSError, IOError):
            if fallback is None:
                error = "source code for class {} could not be retrieved".format(
                    repr(obj.__name__)
                )
                exc = QualnameError(error)
                raise_from(exc, None)
                raise exc
            else:
                return fallback
    elif inspect.isfunction(obj) or inspect.ismethod(obj):
        if hasattr(obj, "im_func"):
            # Extract function from unbound method (Python 2).
            obj = obj.im_func  # type: ignore
        try:
            code = obj.__code__
        except AttributeError:
            code = obj.func_code  # type: ignore
        lineno = code.co_firstlineno
    else:
        if fallback is None:
            error = "source code could not be retrieved for {}".format(
                repr(obj.__name__)
            )
            raise QualnameError(error)
        else:
            return fallback

    # Parse the source file to figure out what the qualified name should be.
    if filename in _cache:
        qualnames = _cache[filename]
    else:
        try:
            with open(filename, "r") as fp:
                source = fp.read()
        except (OSError, IOError) as e:
            if fallback is None:
                error = "could not read source code at {}; {}".format(repr(filename), e)
                exc = QualnameError(error)
                raise_from(exc, None)
                raise exc
            else:
                return fallback
        node = ast.parse(source, filename)
        visitor = _Visitor()
        visitor.visit(node)
        qualnames = _cache[filename] = visitor.qualnames

    # Get qualified name from parsing results.
    qualified_name = qualnames.get(lineno, None)
    if qualified_name is None:
        if fallback is None:
            error = "qualified name could not be retrieved from {} source code".format(
                repr(obj.__name__)
            )
            raise QualnameError(error)
        else:
            return fallback

    return qualified_name


class QualnameMeta(type):
    """Implements qualified name feature for Python 2 classes based on AST parsing."""

    if not _HAS_NATIVE_QUALNAME:

        def __getattr__(cls, name):
            if name == _QUALNAME_ATTR:

                # Try to use cached.
                qualified_name = cls.__dict__.get(_QUALNAME_CACHE_ATTR, None)
                if qualified_name is not None:
                    return qualified_name

                # Get it using AST parsing and cache it.
                qualified_name = qualname(cls, force_ast=True)
                type.__setattr__(cls, _QUALNAME_CACHE_ATTR, qualified_name)
                return qualified_name

            else:
                try:
                    return super(QualnameMeta, cls).__getattr__(name)
                except AttributeError:
                    pass
                return type.__getattribute__(cls, name)

        def __delattr__(cls, name):
            if name == _QUALNAME_ATTR:
                error = "can't delete {}.{}".format(cls.__name__, _QUALNAME_ATTR)
                raise TypeError(error)
            else:
                super(QualnameMeta, cls).__delattr__(name)

        def __repr__(cls):
            # type: () -> str
            module = cls.__module__
            name = qualname(cls, fallback=cls.__name__)
            path = ".".join(p for p in (module, name) if p)
            return "<class{space}{quote}{path}{quote}>".format(
                space=" " if path else "",
                quote="'" if path else "",
                path=path,
            )
