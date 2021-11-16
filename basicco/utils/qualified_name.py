"""
Python 2.7 compatible way to find the qualified name inspired by wbolster/qualname.
"""

import ast
import inspect
from typing import TYPE_CHECKING

from six import raise_from

if TYPE_CHECKING:
    from typing import Callable, Dict, Optional

__all__ = ["get_qualified_name", "QualnameError"]


_cache = {}  # type: Dict[str, Dict[int, str]]


class QualnameError(Exception):
    """Raised when could not get the qualified name from AST parsing."""


def get_qualified_name(obj, fallback=None, force_ast=False):
    # type: (Callable, Optional[str], bool) -> str
    """
    Try to find out the qualified name for a class or function.
    This function uses ast parsing in Python 2.7 to try to replicate the qualified name
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
    if (
        not callable(obj)
        or not hasattr(obj, "__name__")
        or not hasattr(obj, "__module__")
    ):
        error = "can't determine qualified name for instances of {}".format(
            repr(type(obj).__name__)
        )
        raise TypeError(error)
    obj_name = obj.__name__
    obj_module = obj.__module__  # type: ignore

    # Native qualified name or manually defined.
    if not force_ast:
        try:
            return getattr(obj, "__qualname__")
        except QualnameError:  # in case this function gets called when getting the attr
            if fallback is not None:
                return fallback
            else:
                raise
        except AttributeError:
            pass

    # Try to match the root of the module in case the object is not nested.
    try:
        module = __import__(obj_module, fromlist=[obj_name])
    except ImportError as e:
        error = "couldn't import module {} for {}; {}".format(
            repr(obj_module), repr(obj_name), e
        )
        exc = QualnameError(error)
        raise_from(exc, None)
        raise exc
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

    # Sort list of line numbers based on the one found via inspection.
    if qualified_names:
        linenos = sorted(
            qualified_names,
            reverse=True,
            key=lambda k: (
                k - lineno if k >= lineno else max(qualified_names) + (lineno - k)
            ),
        )
    else:
        linenos = []

    # Iterate over possible line numbers.
    while linenos:
        current_lineno = linenos.pop()

        # Get qualified name from parsing results.
        qualified_name = qualified_names.get(current_lineno, None)
        if qualified_name is None:
            if fallback is None:
                error = (
                    "qualified name could not be retrieved from source code for {}"
                ).format(repr(obj_name))
                raise QualnameError(error)
            else:
                return fallback

        # Verify qualified name.
        if qualified_name and "<locals>" not in qualified_name:
            qualified_name_parts = qualified_name.split(".")
            test_obj = module
            while qualified_name_parts:
                part = qualified_name_parts.pop(0)
                try:
                    test_obj = getattr(test_obj, part)
                except AttributeError:
                    break
            else:

                # Extract function from unbound method (Python 2).
                if hasattr(test_obj, "im_func"):
                    test_obj = test_obj.im_func  # type: ignore

                # Return only confirmed to be the same exact object.
                if test_obj is obj and test_obj:
                    return qualified_name

    # No way to reliably retrieve qualified name.
    error = "qualified name could not be retrieved from source code for {}".format(
        repr(obj.__name__)
    )
    raise QualnameError(error)


class _Visitor(ast.NodeVisitor):
    """AST node visitor that stores qualified names."""

    def __init__(self):
        self.stack = []
        self.qualified_names = {}

    def store_qualified_name(self, lineno):
        qn = ".".join(n for n in self.stack)
        self.qualified_names[lineno] = qn

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.store_qualified_name(node.lineno)
        self.stack.append("<locals>")
        self.generic_visit(node)
        self.stack.pop()
        self.stack.pop()

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        self.store_qualified_name(node.lineno)
        self.generic_visit(node)
        self.stack.pop()
