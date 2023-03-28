"""Dynamic class generation."""

import types

import six
from tippo import Any, Dict, Iterable, Mapping, Type, TypeVar, Union

from .caller_module import caller_module
from .init_subclass import InitSubclassMeta

__all__ = ["make_cls"]


_T = TypeVar("_T")


def make_cls(
    qualified_name,  # type: str
    bases=None,  # type: Union[Iterable[Type[Any]], None]
    meta=None,  # type: Union[Type[Any], None]
    dct=None,  # type: Union[Mapping[str, Any], None]
    kwargs=None,  # type: Union[Mapping[str, Any], None]
    module=None,  # type: Union[str, None]
):
    # type: (...) -> Type[_T]
    """
    Dynamically make a class.

    :param qualified_name: Qualified name.
    :param bases: Bases.
    :param meta: Metaclass.
    :param dct: Class body dictionary.
    :param kwargs: Class keyword arguments.
    :param module: Class module.
    :return: Generated class.
    """
    if bases is None:
        bases = (object,)
    else:
        bases = tuple(bases)

    if dct is None:
        dct_ = {}
    else:
        dct_ = dict(dct)

    if kwargs is None:
        kwargs = {}
    else:
        kwargs = dict(kwargs)

    if module is None:
        module = caller_module()

    name = qualified_name.split(".")[-1]
    dct_["__qualname__"] = qualified_name
    dct_["__module__"] = module

    if hasattr(types, "new_class"):
        if meta is not None:
            kwargs["metaclass"] = meta

        def exec_body(namespace):
            # type: (Dict[str, Any]) -> Dict[str, Any]
            """Construct class body."""
            for key, value in six.iteritems(dct_):
                namespace[key] = value
            return namespace

        assert bases is not None
        cls = types.new_class(name, bases, kwargs, exec_body)  # noqa
    else:
        if meta is not None:
            bases = (six.with_metaclass(meta, *bases),)

        if kwargs and any(isinstance(b, InitSubclassMeta) for b in bases):
            dct_["__kwargs__"] = kwargs
            kwargs = {}

        cls = type(name, bases, dct_, **kwargs)

    type.__setattr__(cls, "__qualname__", qualified_name)
    type.__setattr__(cls, "__module__", module)

    return cls  # noqa
