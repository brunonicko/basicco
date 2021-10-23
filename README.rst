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

`Basicco` provides a `Base`_ class and lower-level utilities to enhance compatibility,
readability, and validation.

Motivation
----------
While developing Python code for Visual Effects pipelines, I found myself having to
write the same boiler-plates over and over again.

Overview
--------
  - Cross-compatibility
    - abstractmethod decorator
    - Pickle and slots
  - Readability, shorter code
    - frozen decorator
  - Runtime checking, not for speed
    - frozen decorator
    - final decorator

Base
----
The `Base`_ class enables the use of functionalities provided by `Basicco`.
In most of the cases, it's a simple drop-in replacement for `object`:

.. code:: python

    >>> from basicco import Base
    >>> class Asset(Base):
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
    AttributeError: 'Asset' is frozen, can't set class attribute

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

This decorator is still recognized by Mypy static type checking, and also prevents
subclassing or member overrides during runtime:

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
Same as the
`abc.abstractmethod <https://docs.python.org/3/library/abc.html#abc.abstractmethod>`_
decorator.

Can be used directly on methods but also on properties, classmethods, and staticmethods
(even in Python 2.7).

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

\__qualname__
^^^^^^^^^^^^^
Support for qualified name falling back to AST parsing of the source code.

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
Support for the `typing.Generic` class.

Utilities
---------

import_path
^^^^^^^^^^^

qualname
^^^^^^^^

reducer
^^^^^^^

slots
^^^^^
