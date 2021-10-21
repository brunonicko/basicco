"""Python 2 compatible way to find the qualified name based on wbolster/qualname."""

from six import raise_from

from .utils.qualname import qualname, QualnameError

__all__ = ["qualname", "QualnameError", "QualnameMeta"]


class QualnameMeta(type):
    """Implements qualified name feature for Python 2 classes based on AST parsing."""

    if not hasattr(type, "__qualname__"):

        def __getattr__(cls, name):
            if name == "__qualname__":

                # Try to use cached.
                qualified_name = cls.__dict__.get("__qualname", None)
                if qualified_name is not None:
                    return qualified_name

                # Get it using AST parsing and cache it.
                try:
                    qualified_name = qualname(cls, force_ast=True)
                except QualnameError as e:

                    # Try to check if the qualname is the same as the name.
                    try:
                        module = __import__(cls.__module__, fromlist=[cls.__name__])
                        if getattr(module, cls.__name__) is not cls:
                            raise ImportError()
                    except (ImportError, AttributeError):

                        # Could not get it, reraise QualnameError.
                        raise_from(e, None)
                        raise e

                    else:

                        # Return without caching (in case the name changes).
                        return cls.__name__

                # Cache it and return.
                type.__setattr__(cls, "__qualname", qualified_name)
                return qualified_name

            else:
                try:
                    return super(QualnameMeta, cls).__getattr__(name)
                except AttributeError:
                    pass
                return type.__getattribute__(cls, name)

        def __delattr__(cls, name):
            if name == "__qualname__":
                error = "can't delete {}.{}".format(cls.__name__, "__qualname__")
                raise TypeError(error)
            else:
                super(QualnameMeta, cls).__delattr__(name)
