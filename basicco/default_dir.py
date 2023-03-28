"""
Backport of Python 3's implementation of
`object.__dir__ <https://docs.python.org/3/reference/datamodel.html#object.__dir__>`_.
"""

import six
from tippo import Any, Dict, Tuple, Type, TypeVar

from .dynamic_code import generate_unique_filename, make_function
from .get_mro import get_mro

__all__ = ["DefaultDirMeta", "DefaultDir"]


class DefaultDirMeta(type):
    """Backports the base implementation of `__dir__`."""

    if not hasattr(object, "__dir__"):

        @staticmethod
        def __new__(
            mcs,  # type: Type[_DDM]
            name,  # type: str
            bases,  # type: Tuple[Type[Any], ...]
            dct,  # type: Dict[str, Any]
            **kwargs  # type: Any
        ):
            # type: (...) -> _DDM
            cls = super(DefaultDirMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)
            if not hasattr(cls, "__dir__"):
                script = "\n".join(
                    (
                        "def __dir__(self):",
                        "    cls = type(self)",
                        "    members = set()",
                        '    if hasattr(self, "__dict__"):',
                        "        members.update(self.__dict__)",
                        "    for base in get_mro(cls):",
                        "        members.update(base.__dict__)",
                        "    return sorted(members)",
                    )
                )
                func_name = "__dir__"
                module = dct.get("__module__", None)
                func = make_function(
                    name=func_name,
                    script=script,
                    globs={"get_mro": get_mro},
                    filename=generate_unique_filename(
                        func_name, module=module, owner_name=name
                    ),
                    module=module,
                )
                type.__setattr__(cls, func_name, func)
            return cls


_DDM = TypeVar("_DDM", bound=DefaultDirMeta)


class DefaultDir(six.with_metaclass(DefaultDirMeta, object)):
    """Backports the base implementation of `__dir__`."""

    __slots__ = ()
