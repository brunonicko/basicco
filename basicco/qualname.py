"""Python-2 compatile way of finding the qualified name of a class/method."""

import ast
import inspect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Dict

__all__ = ["qualname"]

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


def qualname(obj, force_ast=False):
    # type: (Callable, bool) -> str
    """
    Try to find out the qualified name for a class or function.
    This function uses ast parsing in Python 2 to try to replicate the qualified name
    functionality available in Python 3.3+.

    :param obj: Function or class.
    :type obj: function or type

    :param force_ast: Force use AST parser to get qualified name from code.
    :type force_ast: bool

    :return: Qualified name (or None if not available).
    :rtype: str

    :raises TypeError: Provided object is not a function or a class.
    """

    # Not available for non-callables.
    if not callable(obj) or not hasattr(obj, "__name__"):
        error = "can't determine qualified name for instances of {}".format(
            repr(type(obj).__name__)
        )
        raise TypeError(error)

    # Already defined (Python 3.3+ or manually defined).
    if not force_ast and hasattr(obj, "__qualname__"):
        return obj.__qualname__

    # Fallback name if we can't reach the definition in the code.
    fallback = obj.__name__

    # Get source file name.
    try:
        filename = inspect.getsourcefile(obj)
        if filename is None:
            raise TypeError()
    except TypeError:
        return fallback

    # Get line number.
    if inspect.isclass(obj):
        try:
            _, lineno = inspect.getsourcelines(obj)
        except (OSError, IOError):
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
        return fallback

    # Parse the source file to figure out what the __qualname__ should be.
    if filename in _cache:
        qualnames = _cache[filename]
    else:
        with open(filename, "r") as fp:
            source = fp.read()
        node = ast.parse(source, filename)
        visitor = _Visitor()
        visitor.visit(node)
        qualnames = _cache[filename] = visitor.qualnames

    return qualnames.get(lineno, fallback)
