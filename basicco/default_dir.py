"""
Backport of Python 3's implementation of
`object.__dir__ <https://docs.python.org/3/reference/datamodel.html#object.__dir__>`_ for Python 2.7.
"""

import inspect

import six

from .dynamic_code import generate_unique_filename, make_function

__all__ = ["DefaultDirMeta", "DefaultDir"]


class DefaultDirMeta(type):
    """Metaclass that backports the base implementation of `__dir__` for Python 2.7."""

    if not hasattr(object, "__dir__"):

        @staticmethod
        def __new__(mcs, name, bases, dct, **kwargs):
            cls = super(DefaultDirMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            if not hasattr(cls, "__dir__"):
                script = "\n".join(
                    (
                        "def __dir__(self):",
                        "    cls = type(self)",
                        "    members = set()",
                        '    if hasattr(self, "__dict__"):',
                        "        members.update(self.__dict__)",
                        "    for base in inspect.getmro(cls):",
                        "        members.update(base.__dict__)",
                        "    return sorted(members)",
                    )
                )
                func_name = "__dir__"
                module = dct.get("__module__", None)
                func = make_function(
                    name=func_name,
                    script=script,
                    globs={"inspect": inspect},
                    filename=generate_unique_filename(func_name, module=module, owner_name=name),
                    module=module,
                )
                type.__setattr__(cls, func_name, func)
            return cls


class DefaultDir(six.with_metaclass(DefaultDirMeta, object)):
    """Class that backports the base implementation of `__dir__` for Python 2.7."""

    __slots__ = ()
