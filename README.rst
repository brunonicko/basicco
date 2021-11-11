Basicco
=======
.. image:: https://github.com/brunonicko/basicco/workflows/MyPy/badge.svg
   :target: https://github.com/brunonicko/basicco/actions?query=workflow%3AMyPy

.. image:: https://github.com/brunonicko/basicco/workflows/Lint/badge.svg
   :target: https://github.com/brunonicko/basicco/actions?query=workflow%3ALint

.. image:: https://github.com/brunonicko/basicco/workflows/Tests/badge.svg
   :target: https://github.com/brunonicko/basicco/actions?query=workflow%3ATests

.. image:: https://readthedocs.org/projects/basicco/badge/?version=stable
   :target: https://basicco.readthedocs.io/en/stable/

.. image:: https://img.shields.io/github/license/brunonicko/basicco?color=light-green
   :target: https://github.com/brunonicko/basicco/blob/master/LICENSE

.. image:: https://static.pepy.tech/personalized-badge/basicco?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads
   :target: https://pepy.tech/project/basicco

.. image:: https://img.shields.io/pypi/pyversions/basicco?color=light-green&style=flat
   :target: https://pypi.org/project/basicco/

Motivation
----------
While developing Python software for Visual Effects pipelines, I found myself having to
write the same boiler-plate code over and over again, as well as struggling with
compatibility issues and feature gaps between Python 2 and Python 3.

So I decided to tackle it at the `Base`_, literally.

Overview
--------
`Basicco` provides a `Base`_ class and multiple lower-level `Utilities`_ to enhance
code compatibility, readability, and validation.

Base
----
The `Base`_ class enables the use of functionalities provided by `Basicco`.
It is designed to be a simple drop-in replacement for `object` in your base classes:

.. code:: python

    >>> from basicco import Base
    >>> class Asset(Base):  # inherit from Base instead of object
    ...     pass
    ...

frozen
^^^^^^
Class decorator that prevents changing the attribute values for classes and/or their
instances after they have been initialized.

.. code:: python

    >>> from basicco import Base, frozen
    >>> @frozen(classes=True)
    ... class Asset(Base):
    ...     typename = "geometry"
    ...
    >>> Asset.typename = "nurbs"
    Traceback (most recent call last):
    AttributeError: class 'Asset' is frozen, can't set class attribute

.. code:: python

    >>> from basicco import Base, frozen
    >>> @frozen(instances=True)
    ... class Asset(Base):
    ...     def __init__(self, name, typename):
    ...         self.name = name
    ...         self.typename = typename
    ...
    >>> asset = Asset("cube", "geometry")
    >>> asset.name = "sphere"
    Traceback (most recent call last):
    AttributeError: instances of 'Asset' are frozen, can't set attribute

final
^^^^^
Runtime-checked version of the
`typing.final <https://docs.python.org/3/library/typing.html#typing.final>`_ decorator.

Can be used directly on methods but also on properties, classmethods, and staticmethods
(even in Python 2.7).

This decorator is still recognized by Mypy static type checking, and it also prevents
subclassing and/or member overrides during runtime:

.. code:: python

    >>> from basicco import Base, final
    >>> @final
    ... class Asset(Base):
    ...     pass
    ...
    >>> class SubAsset(Asset):
    ...     pass
    ...
    Traceback (most recent call last):
    TypeError: can't subclass final class 'Asset'

.. code:: python

    >>> from basicco import Base, final
    >>> class Asset(Base):
    ...     @final
    ...     def method(self):
    ...         pass
    ...
    >>> class SubAsset(Asset):
    ...     def method(self):
    ...         pass
    Traceback (most recent call last):
    TypeError: can't override final member 'method'

.. code:: python

    >>> from basicco import Base, final
    >>> class Asset(Base):
    ...     @property
    ...     @final
    ...     def prop(self):
    ...         pass
    ...
    >>> class SubAsset(Asset):
    ...     @property
    ...     def prop(self):
    ...         pass
    Traceback (most recent call last):
    TypeError: can't override final member 'prop'

abstract
^^^^^^^^
Augmented version of the
`abc.abstractmethod <https://docs.python.org/3/library/abc.html#abc.abstractmethod>`_
decorator.

Can be used directly on methods but also on classes, properties, classmethods, and
staticmethods (even in Python 2.7).

.. code:: python

    >>> from basicco import Base, abstract
    >>> class Asset(Base):
    ...     @abstract
    ...     def method(self):
    ...         pass
    ...
    ...     @property
    ...     @abstract
    ...     def prop(self):
    ...         return None
    ...
    >>> Asset()
    Traceback (most recent call last):
    TypeError: Can't instantiate abstract class Asset with abstract methods method, prop

.. code:: python

    >>> from basicco import Base, abstract
    >>> @abstract
    ... class Asset(Base):
    ...     pass
    ...
    >>> Asset()
    Traceback (most recent call last):
    TypeError: can't instantiate abstract class 'Asset'

\__qualname__
^^^^^^^^^^^^^
Support for qualified name falling back to AST parsing of the source code and/or class
definition hierarchy.

Bases have a `__qualname__` attribute (even in Python 2.7):

.. code:: python

    >>> from basicco import Base
    >>> class Asset(Base):
    ...     class Config(Base):
    ...         pass
    ...
    >>> Asset.Config.__qualname__
    'Asset.Config'

\__reduce__
^^^^^^^^^^^
Support for pickling instances of classes that utilize qualified name and/or slots.

Slotted and/or nested bases can be pickled (even in Python 2.7):

.. code:: python

    >>> import pickle
    >>> from basicco import Base
    >>> class Asset(Base):
    ...     class Config(Base):
    ...         __slots__ = ("name", "version")
    ...         def __init__(self):
    ...             self.name = "cube"
    ...             self.version = 2
    ...
    >>> pickled = pickle.dumps(Asset.Config())
    >>> pickle.loads(pickled)
    <__main__.Asset.Config object at ...>

generic
^^^^^^^
Better support for the `typing.Generic` class (even in Python 2.7).

Utilities
---------

import_path
^^^^^^^^^^^
Generate import paths with support for qualified names and import from them.

.. code:: python

    >>> from basicco.utils.import_path import get_import_path, import_from_path
    >>> class Asset(Base):
    ...     class Config(Base):
    ...         pass
    ...
    >>> get_import_path(Asset.Config)
    '__main__|Asset.Config'
    >>> import_from_path('__main__|Asset.Config')
    <class '__main__.Asset.Config'>

qualified_name
^^^^^^^^^^^^^^

reducer
^^^^^^^

slots
^^^^^
