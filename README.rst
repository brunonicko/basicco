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
While developing Python software for Visual Effects pipelines, I found myself writing the same boiler-plate utilities
over and over again. So I decided to implement solutions for those issues at the `Base`_, quite literally.

Overview
--------
`Basicco` provides a `Base`_ classes and multiple lower-level `Utilities`_ that enhance code readability and validation.

Base
----
The `Base`_ class is designed to be a simple drop-in replacement for `object` when defining your base classes:

.. code:: python

    >>> from basicco import Base
    >>> class Asset(Base):  # inherit from Base instead of object
    ...     pass
    ...

Utilities
---------

abstract_class
^^^^^^^^^^^^^^
Decorator that prevents an abstract class from being instantiated.

.. code:: python

    >>> from basicco.utils.abstract_class import abstract_class
    >>> @abstract_class
    ... class Abstract:
    ...     pass
    ...
    >>> class Concrete(Abstract):
    ...     pass
    ...
    >>> concrete = Concrete()
    >>> abstract = Abstract()
    Traceback (most recent call last):
    NotImplementedError: can't instantiate abstract class 'Abstract'

caller_module
^^^^^^^^^^^^^
Retrieve the caller's module name.

.. code:: python

    >>> from basicco.utils.caller_module import caller_module
    >>> def do_something():
    ...     return f"I was called by {caller_module()}"
    ...
    >>> do_something()
    'I was called by __main__'

custom_repr
^^^^^^^^^^^
Custom representation functions.

.. code:: python

    >>> from basicco.utils.custom_repr import mapping_repr
    >>> dct = {"a": 1, "b": 2}
    >>> mapping_repr(dct, prefix="<", suffix=">", template="{key}={value}", sorting=True)
    "<'a'=1, 'b'=2>"

.. code:: python

    >>> from basicco.utils.custom_repr import iterable_repr
    >>> tup = ("a", "b", "c", 1, 2, 3)
    >>> iterable_repr(tup, prefix="<", suffix=">", value_repr=str)
    '<a, b, c, 1, 2, 3>'

explicit_hash
^^^^^^^^^^^^^
Metaclass that forces `__hash__` to be declared when `__eq__` is declared.

.. code:: python

    >>> from basicco.utils.explicit_hash import ExplicitHashMeta
    >>> class Asset(metaclass=ExplicitHashMeta):
    ...     def __eq__(self, other):
    ...         pass
    ...
    Traceback (most recent call last):
    TypeError: declared '__eq__' in 'Asset', but didn't declare '__hash__'

import_path
^^^^^^^^^^^
Generate importable dot paths and import from them.

.. code:: python

    >>> from basicco.utils.import_path import get_path, import_path
    >>> class Asset(Base):
    ...     class Config(Base):
    ...         pass
    ...
    >>> get_path(Asset.Config)
    '__main__.Asset.Config'
    >>> import_path("__main__.Asset.Config")
    <class '__main__.Asset.Config'>

namespace
^^^^^^^^^
Wraps a dictionary/mapping and provides attribute-style access to it.

.. code:: python

    >>> from basicco.utils.namespace import Namespace
    >>> ns = Namespace({"bar": "foo"})
    >>> ns.foo = "bar"
    >>> ns.foo
    'bar'
    >>> ns.bar
    'foo'

Also provides a `NamespacedMeta` metaclass for adding a `__namespace__` private property that is unique to each class.

.. code:: python

    >>> from basicco.utils.namespace import NamespacedMeta
    >>> class Asset(metaclass=NamespacedMeta):
    ...     pass
    ...
    >>> Asset.__namespace__.foo = "bar"

privatize
^^^^^^^^^
Functions to privatize/deprivatize member names.

.. code:: python

    >>> from basicco.utils.privatize import privatize_name, deprivatize_name
    >>> privatize_name("Foo", "__member")
    '_Foo__member'
    >>> deprivatize_name("_Foo__member")
    ('__member', 'Foo')

recursive_repr
^^^^^^^^^^^^^^
Decorator that prevents infinite recursion for `__repr__` methods.

.. code:: python

    >>> from basicco.utils.recursive_repr import recursive_repr
    >>> class MyClass(object):
    ...
    ...     @recursive_repr
    ...     def __repr__(self):
    ...         return f"MyClass<{self!r}>"
    ...
    >>> my_obj = MyClass()
    >>> repr(my_obj)
    'MyClass<...>'

runtime_final
^^^^^^^^^^^^^
Runtime-checked version of the `typing.final <https://docs.python.org/3/library/typing.html#typing.final>`_ decorator.

Can be used on methods, properties, classmethods, staticmethods, and classes that have `FinalizedMeta` as a metaclass.
It is also recognized by static type checkers and prevents subclassing and/or member overriding during runtime:

.. code:: python

    >>> from basicco.utils.runtime_final import FinalizedMeta, final
    >>> @final
    ... class Asset(metaclass=FinalizedMeta):
    ...     pass
    ...
    >>> class SubAsset(Asset):
    ...     pass
    ...
    Traceback (most recent call last):
    TypeError: can't subclass final class 'Asset'

.. code:: python

    >>> from basicco.utils.runtime_final import FinalizedMeta, final
    >>> class Asset(metaclass=FinalizedMeta):
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

    >>> from basicco.utils.runtime_final import FinalizedMeta, final
    >>> class Asset(metaclass=FinalizedMeta):
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

unique_iterator
^^^^^^^^^^^^^^^
Iterator that yields unique values.

.. code:: python

    >>> from basicco.utils.unique_iterator import unique_iterator
    >>> list(unique_iterator([1, 2, 3, 3, 4, 4, 5]))
    [1, 2, 3, 4, 5]
