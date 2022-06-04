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
While developing Python software for Visual Effects pipelines, I found myself writing the same general lower-level
utilities over and over again. So I decided to package those up into `Basicco`.

Overview
--------
`Basicco` provides a collection of lower-level `Utilities`_ that enhance code readability and validation.

Utilities
---------

abstract_class
^^^^^^^^^^^^^^
Decorator that prevents an abstract class from being instantiated.

This works even if the class doesn't have any abstract methods or properties.
Concrete subclasses (non-decorated) are able to be instantiated without any issues.

.. code:: python

    >>> from basicco.abstract_class import abstract_class
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

    >>> from basicco.caller_module import caller_module
    >>> def do_something():
    ...     return f"I was called by {caller_module()}"
    ...
    >>> do_something()
    'I was called by __main__'

custom_repr
^^^^^^^^^^^
Custom representation functions.

.. code:: python

    >>> from basicco.custom_repr import mapping_repr
    >>> dct = {"a": 1, "b": 2}
    >>> mapping_repr(dct, prefix="<", suffix=">", template="{key}={value}", sorting=True)
    "<'a'=1, 'b'=2>"

.. code:: python

    >>> from basicco.custom_repr import iterable_repr
    >>> tup = ("a", "b", "c", 1, 2, 3)
    >>> iterable_repr(tup, prefix="<", suffix=">", value_repr=str)
    '<a, b, c, 1, 2, 3>'

explicit_hash
^^^^^^^^^^^^^
Metaclass that forces `__hash__` to be declared when `__eq__` is declared.

.. code:: python

    >>> from basicco.explicit_hash import ExplicitHashMeta
    >>> class Asset(metaclass=ExplicitHashMeta):
    ...     def __eq__(self, other):
    ...         pass
    ...
    Traceback (most recent call last):
    TypeError: declared '__eq__' in 'Asset' but didn't declare '__hash__'

import_path
^^^^^^^^^^^
Generate importable dot paths and import from them.

.. code:: python

    >>> import itertools
    >>> from basicco.import_path import get_path, import_path
    >>> get_path(itertools.chain)
    'itertools.chain'
    >>> import_path("itertools.chain")
    <class 'itertools.chain'>

.. code:: python

    >>> from basicco.import_path import extract_generic_paths
    >>> extract_generic_paths("Tuple[int, str]")
    ('Tuple', ('int', 'str'))

namespace
^^^^^^^^^
Wraps a dictionary/mapping and provides attribute-style access to it.

.. code:: python

    >>> from basicco.namespace import Namespace
    >>> ns = Namespace({"bar": "foo"})
    >>> ns.bar
    'foo'

.. code:: python

    >>> from basicco.namespace import MutableNamespace
    >>> ns = MutableNamespace({"bar": "foo"})
    >>> ns.foo = "bar"
    >>> ns.foo
    'bar'
    >>> ns.bar
    'foo'

Also provides a `NamespacedMeta` metaclass for adding a `__namespace__` private property that is unique to each class.

.. code:: python

    >>> from basicco.namespace import NamespacedMeta
    >>> class Asset(metaclass=NamespacedMeta):
    ...     pass
    ...
    >>> Asset.__namespace__.foo = "bar"

privatize
^^^^^^^^^
Functions to privatize/deprivatize member names.

.. code:: python

    >>> from basicco.privatize import privatize, deprivatize
    >>> privatize("__member", "Foo")
    '_Foo__member'
    >>> deprivatize("_Foo__member")
    ('__member', 'Foo')

recursive_repr
^^^^^^^^^^^^^^
Decorator that prevents infinite recursion for `__repr__` methods.

.. code:: python

    >>> from basicco.recursive_repr import recursive_repr
    >>> class MyClass:
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

    >>> from basicco.runtime_final import FinalizedMeta, final
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

    >>> from basicco.runtime_final import FinalizedMeta, final
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

    >>> from basicco.runtime_final import FinalizedMeta, final
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

    >>> from basicco.unique_iterator import unique_iterator
    >>> list(unique_iterator([1, 2, 3, 3, 4, 4, 5]))
    [1, 2, 3, 4, 5]
