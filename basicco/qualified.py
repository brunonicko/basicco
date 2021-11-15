"""Python 2.7 compatible way to find the qualified name based on wbolster/qualname."""

from six import raise_from, iteritems

from .utils.qualified_name import get_qualified_name, QualnameError

__all__ = ["get_qualified_name", "QualnameError", "QualifiedMeta"]

_PARENT_ATTRIBUTE = "_QualifiedMeta__parent"
_QUALNAME_ATTRIBUTE = "_QualifiedMeta__qualname"


class QualifiedMeta(type):
    """Implements qualified name feature for Python 2.7 classes based on AST parsing."""

    # Only implement if current Python does not natively support qualified names.
    if not hasattr(type, "__qualname__"):

        @staticmethod
        def __new__(mcs, name, bases, dct, **kwargs):

            # Qualified name was manually specified in the class body.
            manual_qualified_name = dct.pop("__qualname__", None)
            if manual_qualified_name is not None:
                dct = dict(dct)
                dct[_QUALNAME_ATTRIBUTE] = manual_qualified_name

            # Build class.
            cls = super(QualifiedMeta, mcs).__new__(mcs, name, bases, dct, **kwargs)

            # Look for classes defined inside of this class' body, mark as a parent.
            for attribute_name, value in iteritems(dct):
                if (
                    isinstance(value, QualifiedMeta)
                    and value.__name__ == attribute_name
                    and _PARENT_ATTRIBUTE not in value.__dict__
                ):
                    try:
                        module = __import__(value.__module__, fromlist=[attribute_name])
                        if getattr(module, attribute_name) is value:
                            continue
                    except (ImportError, AttributeError):
                        type.__setattr__(value, _PARENT_ATTRIBUTE, cls)

            return cls

        def __get_qualified_name(cls, use_cache=True):

            # Try to use cached.
            if use_cache:
                qualified_name = cls.__dict__.get(_QUALNAME_ATTRIBUTE, None)
                if qualified_name is not None:
                    return qualified_name

            # Try to get it using AST parsing. Forcing AST parsing avoids recursion.
            try:
                qualified_name = get_qualified_name(cls, force_ast=True)
            except QualnameError as e:

                # Try to use parent (for when running interactively).
                if _PARENT_ATTRIBUTE in cls.__dict__:
                    parent = cls.__dict__[_PARENT_ATTRIBUTE]
                    if parent is not None:
                        assert isinstance(parent, QualifiedMeta)

                        # Compose qualified name with parent's.
                        try:
                            parent_qualified_name = parent.__get_qualified_name(
                                use_cache=False
                            )
                        except (AttributeError, QualnameError):
                            pass
                        else:
                            qualified_name = "{}.{}".format(
                                parent_qualified_name, cls.__name__
                            )

                            # Cache it and return.
                            if use_cache:
                                type.__setattr__(
                                    cls, _QUALNAME_ATTRIBUTE, qualified_name
                                )
                            return qualified_name

                # Could not get it, re-raise QualnameError.
                raise_from(e, None)
                raise e

            else:

                # Cache it and return.
                if use_cache:
                    type.__setattr__(cls, _QUALNAME_ATTRIBUTE, qualified_name)
                return qualified_name

        @property  # type: ignore
        def __qualname__(cls):  # type: ignore
            return cls.__get_qualified_name()

        @__qualname__.setter
        def __qualname__(cls, value):
            type.__setattr__(cls, _QUALNAME_ATTRIBUTE, value)

        @__qualname__.deleter
        def __qualname__(cls):
            error = "can't delete {}.__qualname__".format(cls.__name__)
            raise TypeError(error)
