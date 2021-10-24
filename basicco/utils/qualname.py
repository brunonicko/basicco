"""Python 2 compatible way to find the qualified name based on wbolster/qualname."""

import ast
import inspect
from typing import TYPE_CHECKING

from six import raise_from

if TYPE_CHECKING:
    from typing import Callable, Dict, Optional

__all__ = ["qualname", "QualnameError"]


_cache = {}  # type: Dict[str, Dict[int, str]]


class QualnameError(Exception):
    """Raised when could not get the qualified name from AST parsing."""


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
    obj_name = obj.__name__

    # Native qualified name or manually defined.
    if not force_ast:
        try:
            return getattr(obj, "__qualname__")
        except QualnameError:
            if fallback is not None:
                return fallback
            else:
                raise
        except AttributeError:
            pass

    # Try to match the root of the module in case object is not nested under anything.
    module_name = getattr(obj, "__module__", None)
    if module_name is not None:
        try:
            module = __import__(module_name, fromlist=[obj_name])
        except ImportError:
            pass
        else:
            if getattr(module, obj_name, None) is obj:
                return obj_name

    # Get source file name.
    try:
        filename = inspect.getsourcefile(obj)
        if filename is None:
            raise TypeError()
    except TypeError:
        if fallback is None:
            error = "couldn't find source code filename for {}".format(repr(obj_name))
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
                    repr(obj_name)
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
            error = "source code could not be retrieved for {}".format(repr(obj_name))
            raise QualnameError(error)
        else:
            return fallback

    # Parse the source file to figure out what the qualified name should be.
    if filename in _cache:
        qualified_names = _cache[filename]
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
        qualified_names = _cache[filename] = visitor.qualified_names

    # Get qualified name from parsing results.
    qualified_name = qualified_names.get(lineno, None)
    if qualified_name is None:
        if fallback is None:
            error = "qualified name could not be retrieved from {} source code".format(
                repr(obj.__name__)
            )
            raise QualnameError(error)
        else:
            return fallback

    return qualified_name


class _Visitor(ast.NodeVisitor):
    """AST node visitor that stores qualified names."""

    def __init__(self):
        self.stack = []
        self.qualified_names = {}

    def store_qualname(self, lineno):
        qn = ".".join(n for n in self.stack)
        self.qualified_names[lineno] = qn

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
