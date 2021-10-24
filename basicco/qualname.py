"""Python 2 compatible way to find the qualified name based on wbolster/qualname."""

from weakref import ref

from six import raise_from, iteritems

from .utils.qualname import qualname, QualnameError

__all__ = ["qualname", "QualnameError", "QualnameMeta"]

_PARENT_ATTRIBUTE_NAME = "_QualnameMeta__parent_ref"
_QUALNAME_CACHE_ATTRIBUTE_NAME = "_QualnameMeta__qualname"


class QualnameMeta(type):
    """Implements qualified name feature for Python 2 classes based on AST parsing."""

    if not hasattr(type, "__qualname__"):

        def __init__(cls, name, bases, dct, **kwargs):
            super(QualnameMeta, cls).__init__(name, bases, dct, **kwargs)
            for attribute_name, value in iteritems(dct):
                if isinstance(value, QualnameMeta):
                    if _PARENT_ATTRIBUTE_NAME not in value.__dict__:
                        type.__setattr__(value, _PARENT_ATTRIBUTE_NAME, cls)

        def __getattr__(cls, name):
            if name == "__qualname__":

                # Try to use cached.
                qualified_name = cls.__dict__.get(_QUALNAME_CACHE_ATTRIBUTE_NAME, None)
                if qualified_name is not None:
                    return qualified_name

                # Try to use parent.
                parent = cls.__dict__.get(_PARENT_ATTRIBUTE_NAME, None)
                if parent is not None:

                    # Compose qualified name with parent's.
                    try:
                        parent_qualified_name = getattr(parent, "__qualname__")
                    except (AttributeError, QualnameError):
                        pass
                    else:
                        qualified_name = "{}.{}".format(
                            parent_qualified_name, cls.__name__
                        )

                        # Cache it and return.
                        type.__setattr__(
                            cls, _QUALNAME_CACHE_ATTRIBUTE_NAME, qualified_name
                        )
                        return qualified_name

                # Get it using AST parsing.
                try:
                    qualified_name = qualname(cls, force_ast=True)
                except QualnameError as e:

                    # Try to check if the qualname is the same as the name.
                    try:
                        module = __import__(cls.__module__, fromlist=[cls.__name__])
                        if getattr(module, cls.__name__) is not cls:
                            raise ImportError()
                    except (ImportError, AttributeError):

                        # Could not get it, re-raise QualnameError.
                        raise_from(e, None)
                        raise e

                    else:

                        # Return without caching (in case the name changes).
                        return cls.__name__

                # Cache it and return.
                type.__setattr__(cls, _QUALNAME_CACHE_ATTRIBUTE_NAME, qualified_name)
                return qualified_name

            else:
                try:
                    super_getattr = super(QualnameMeta, cls).__getattr__  # type: ignore
                except AttributeError:
                    pass
                else:
                    return super_getattr()
                return type.__getattribute__(cls, name)

        def __setattr__(cls, name, value):
            super(QualnameMeta, cls).__delattr__(name)
            if name == "__qualname__":
                if "__qualname__" in cls.__dict__:
                    qualified_name = cls.__dict__["__qualname__"]
                    type.__delattr__(cls, "__qualname__")
                    type.__setattr__(
                        cls, _QUALNAME_CACHE_ATTRIBUTE_NAME, qualified_name
                    )

        def __delattr__(cls, name):
            if name == "__qualname__":
                error = "can't delete {}.{}".format(cls.__name__, "__qualname__")
                raise TypeError(error)
            else:
                super(QualnameMeta, cls).__delattr__(name)
