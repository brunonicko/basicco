"""
Better matches Python 3.7+ behavior on Python 2.7 for
`abstract members <https://docs.python.org/3/library/abc.html>`_ while adding some additional features.
"""

import abc
import functools
import inspect
from abc import abstractmethod as abstract

import six
from tippo import Any, Set

from .dynamic_code import generate_unique_filename, make_function
from .get_mro import get_mro

__all__ = ["abstract", "is_abstract", "AbstractMeta", "Abstract"]

_ABSTRACT_CLASS_TAG = "__isabstractclass__"
_ABSTRACT_METHOD_TAG = "__isabstractmethod__"
_ABSTRACT_METHODS = "__abstractmethods__"


__abstract = abstract

try:
    _ABC = abc.ABC
except AttributeError:
    _ABC = object  # type: ignore


def _abstract(obj):
    """
    Decorate a class or member as abstract.

    :param obj: Class or member.
    :return: Decorated.
    """
    if inspect.isclass(obj):
        original_new = obj.__dict__.get("__new__")
        if isinstance(original_new, staticmethod):
            original_new = original_new.__func__

        script = "\n".join(
            (
                "def __new__(cls, *args, **kwargs):",
                "    if cls.__dict__.get(_ABSTRACT_CLASS_TAG, False):",
                "        abstract_members = getattr(cls, _ABSTRACT_METHODS, ())",
                "        if abstract_members:",
                "            error = 'can\\'t instantiate abstract class {!r} with abstract members {}'.format(",
                "                cls.__name__, ', '.join(repr(m) for m in sorted(abstract_members))",
                "            )",
                "        else:",
                "            error = 'can\\'t instantiate abstract class {!r}'.format(cls.__name__)",
                "        raise TypeError(error)",
                "    elif original_new is not None:",
                "        return original_new(cls, *args, **kwargs)",
                "    else:",
                "        return super(obj, cls).__new__(cls, *args, **kwargs)",
            )
        )
        func_name = "__new__"
        module = obj.__module__
        func = make_function(
            name=func_name,
            script=script,
            globs={
                "_ABSTRACT_CLASS_TAG": _ABSTRACT_CLASS_TAG,
                "_ABSTRACT_METHODS": _ABSTRACT_METHODS,
                "original_new": original_new,
                "obj": obj,
            },
            filename=generate_unique_filename(func_name, module=module, owner_name=obj.__name__),
            module=module,
        )
        func = functools.wraps(original_new or object.__new__)(func)
        type.__setattr__(obj, "__new__", staticmethod(func))
        type.__setattr__(obj, _ABSTRACT_CLASS_TAG, True)

        return obj

    else:
        return __abstract(obj)


globals()["abstract"] = _abstract  # trick IDEs/static type checkers


def is_abstract(obj):
    # type: (Any) -> bool
    """
    Tells whether a class or member is abstract.

    :param obj: Class or member.
    :return: True if abstract.
    """
    if inspect.isclass(obj):
        return obj.__dict__.get(_ABSTRACT_CLASS_TAG, False) or bool(getattr(obj, _ABSTRACT_METHODS, ()))
    else:
        return _is_abstract_member(obj)


def _is_abstract_member(obj):
    # type: (Any) -> bool
    """
    Tells whether a member is abstract.

    :param obj: Member.
    :return: True if abstract.
    """
    _is_abstract = False

    # Descriptor.
    if hasattr(obj, "__get__"):
        _is_abstract |= getattr(obj, _ABSTRACT_METHOD_TAG, False)

        # Has 'fget' getter (property-like).
        if hasattr(obj, "fget"):
            _is_abstract |= getattr(obj.fget, _ABSTRACT_METHOD_TAG, False)

    # Static or class method.
    if isinstance(obj, (staticmethod, classmethod)):
        _is_abstract |= getattr(obj.__func__, _ABSTRACT_METHOD_TAG, False)

    # Regular method.
    if callable(obj):
        _is_abstract |= getattr(obj, _ABSTRACT_METHOD_TAG, False)

    return _is_abstract


class AbstractMeta(abc.ABCMeta):
    """Metaclass that finds abstract members in properties and descriptors for both Python 2.7 and 3.7+."""

    def __init__(cls, name, bases, dct, **kwargs):
        super(AbstractMeta, cls).__init__(name, bases, dct, **kwargs)  # noqa
        cls.__gather_abstract_members()

    def __gather_abstract_members(cls):

        # Iterate over MRO of the class.
        abstract_method_names = set()  # type: Set[str]
        for base in reversed(get_mro(cls)):

            # Find abstract members.
            for member_name, member in six.iteritems(base.__dict__):

                # Keep track.
                if _is_abstract_member(member):
                    abstract_method_names.add(member_name)
                else:
                    abstract_method_names.discard(member_name)

        # Update class information.
        type.__setattr__(cls, _ABSTRACT_METHODS, frozenset(abstract_method_names))

    def __setattr__(cls, name, value):
        super(AbstractMeta, cls).__setattr__(name, value)
        if name in cls.__dict__ and is_abstract(cls.__dict__[name]):
            cls.__gather_abstract_members()

    def __delattr__(cls, name):
        gather = False
        for base in get_mro(cls):
            if name in base.__dict__:
                gather = is_abstract(base.__dict__[name])
                break
        super(AbstractMeta, cls).__delattr__(name)
        if gather:
            cls.__gather_abstract_members()


class Abstract(six.with_metaclass(AbstractMeta, _ABC)):
    """Class that finds abstract members in properties and descriptors for both Python 2.7 and 3.7+."""

    __slots__ = ()
