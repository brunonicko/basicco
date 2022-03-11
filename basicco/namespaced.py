from .utils.namespace import Namespace
from .utils.private_naming import privatize_name

__all__ = [
    "NamespacedMeta",
]

_NAMESPACE_ATTR = privatize_name("NamespacedMeta", "__namespace")


class NamespacedMeta(type):
    @staticmethod
    def __new__(mcs, name, bases, dct, **kwargs):

        # Create new namespace private to this class only.
        dct_copy = dict(dct)
        dct_copy[_NAMESPACE_ATTR] = Namespace()

        return super(NamespacedMeta, mcs).__new__(mcs, name, bases, dct_copy, **kwargs)

    @property
    def _namespace(cls):
        # type: () -> Namespace
        """Class namespace."""
        return cls.__dict__[_NAMESPACE_ATTR]
