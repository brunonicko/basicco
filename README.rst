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
While developing Python software for Visual Effects pipelines, I found myself having to write the same boiler-plate
code over and over again, as well as struggling with compatibility issues and feature gaps between Python 2.7 and
Python 3.7+.

So I decided to implement solutions for those issues at the base, and `basicco` was born.

Overview
--------
`Basicco` provides a collection of lower-level `Utilities`_ that enhance code readability and validation.

Utilities
---------

caller_module
^^^^^^^^^^^^^
Retrieve the caller's module name.

.. code:: python

    >>> from basicco.caller_module import caller_module
    >>> def do_something():
    ...     return "I was called by {}".format(caller_module())
    ...
    >>> do_something()
    'I was called by __main__'

context_vars
^^^^^^^^^^^^
Backport of `contextvars` for Python 2.7 based on `MagicStack/contextvars`.

.. code:: python

    >>> from basicco.context_vars import ContextVar
    >>> my_var = ContextVar("my_var", default="bar")
    >>> token = my_var.set("foo")
    >>> my_var.get()
    'foo'
    >>> my_var.reset(token)
    >>> my_var.get()
    'bar'

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

    >>> import six
    >>> from basicco.explicit_hash import ExplicitHashMeta
    >>> class Asset(six.with_metaclass(ExplicitHashMeta, object)):
    ...     def __eq__(self, other):
    ...         pass
    ...
    Traceback (most recent call last):
    TypeError: declared '__eq__' in 'Asset' but didn't declare '__hash__'

fabricate_value
^^^^^^^^^^^^^^^
Run a value through a callable factory (or None).

.. code:: python

    >>> from basicco.fabricate_value import fabricate_value
    >>> fabricate_value(None, 3)
    3
    >>> fabricate_value(str, 3)
    '3'
    >>> fabricate_value("str", 3)  # use an import path
    '3'

get_mro
^^^^^^^
Get consistent MRO amongst different python versions. This works even with generic classes in Python 2.7.

.. code:: python

    >>> from six import with_metaclass
    >>> from tippo import Generic, TypeVar
    >>> from basicco.get_mro import get_mro
    >>> T = TypeVar("T")
    >>> class MyGeneric(Generic[T]):
    ...     pass
    ...
    >>> class SubClass(MyGeneric[T]):
    ...     pass
    ...
    >>> class Mixed(SubClass[T], MyGeneric[T]):
    ...     pass
    ...
    >>> [c.__name__ for c in get_mro(Mixed)]
    ['Mixed', 'SubClass', 'MyGeneric', 'Generic', 'object']

import_path
^^^^^^^^^^^
Generate importable dot paths and import from them.

.. code:: python

    >>> import itertools
    >>> from basicco.import_path import get_path, import_path
    >>> get_path(itertools.chain)
    'itertools.chain'
    >>> import_path("itertools.chain")
    <... 'itertools.chain'>

.. code:: python

    >>> from basicco.import_path import extract_generic_paths
    >>> extract_generic_paths("Tuple[int, str]")
    ('Tuple', ('int', 'str'))

init_subclass
^^^^^^^^^^^^^
Backport of the functionality of `__init_subclass__` from PEP 487 to Python 2.7.

.. code:: python

    >>> from basicco.init_subclass import InitSubclass
    >>> class Foo(InitSubclass):
    ...     def __init_subclass__(cls, foo=None, **kwargs):
    ...         cls.foo = foo
    ...
    >>> class Bar(Foo):
    ...     __kwargs__ = {"foo": "bar"}
    ...
    >>> Bar.foo
    'bar'

mangling
^^^^^^^^
Functions to mangle/unmangle/extract private names.

.. code:: python

    >>> from basicco.mangling import mangle, unmangle, extract
    >>> mangle("__member", "Foo")
    '_Foo__member'
    >>> unmangle("_Foo__member", "Foo")
    '__member'
    >>> extract("_Foo__member")
    ('__member', 'Foo')

mapping_proxy
^^^^^^^^^^^^^
Mapping Proxy type (read-only) for older Python versions.

.. code:: python

    >>> from basicco.mapping_proxy import MappingProxyType
    >>> internal_dict = {"foo": "bar"}
    >>> proxy_dict = MappingProxyType(internal_dict)
    >>> proxy_dict["foo"]
    'bar'

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

    >>> from six import with_metaclass
    >>> from basicco.namespace import NamespacedMeta
    >>> class Asset(with_metaclass(NamespacedMeta, object)):
    ...     pass
    ...
    >>> Asset.__namespace__.foo = "bar"

qualname
^^^^^^^^
Python 2.7 compatible way of getting the qualified name. Inspired by `wbolster/qualname`.

recursive_repr
^^^^^^^^^^^^^^
Decorator that prevents infinite recursion for `__repr__` methods.

.. code:: python

    >>> from basicco.recursive_repr import recursive_repr
    >>> class MyClass(object):
    ...
    ...     @recursive_repr
    ...     def __repr__(self):
    ...         return "MyClass<{!r}>".format(self)
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

    >>> import six
    >>> from basicco.runtime_final import FinalizedMeta, final
    >>> @final
    ... class Asset(six.with_metaclass(FinalizedMeta, object)):
    ...     pass
    ...
    >>> class SubAsset(Asset):
    ...     pass
    ...
    Traceback (most recent call last):
    TypeError: can't subclass final class 'Asset'

.. code:: python

    >>> import six
    >>> from basicco.runtime_final import FinalizedMeta, final
    >>> class Asset(six.with_metaclass(FinalizedMeta, object)):
    ...     @final
    ...     def method(self):
    ...         pass
    ...
    >>> class SubAsset(Asset):
    ...     def method(self):
    ...         pass
    Traceback (most recent call last):
    TypeError: 'SubAsset' overrides final member 'method' defined by 'Asset'

.. code:: python

    >>> import six
    >>> from basicco.runtime_final import FinalizedMeta, final
    >>> class Asset(six.with_metaclass(FinalizedMeta, object)):
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
    TypeError: 'SubAsset' overrides final member 'prop' defined by 'Asset'

set_name
^^^^^^^^
Backport of the functionality of `__set_name__` from PEP 487 to Python 2.7.

.. code:: python

    >>> from basicco.set_name import SetName
    >>> class Attribute(object):
    ...     def __set_name__(self, owner, name):
    ...         self.owner = owner
    ...         self.name = name
    ...
    >>> class Collection(SetName):
    ...     foo = Attribute()
    ...
    >>> Collection.foo.owner is Collection
    True
    >>> Collection.foo.name
    'foo'

state
^^^^^
Get/update the state of an object, slotted or not (works even in Python 2.7).

.. code:: python

    >>> from basicco.state import get_state
    >>> class Slotted(object):
    ...     __slots__ = ("foo", "bar")
    ...     def __init__(self, foo, bar):
    ...         self.foo = foo
    ...         self.bar = bar
    ...
    >>> slotted = Slotted("a", "b")
    >>> sorted(get_state(slotted).items())
    [('bar', 'b'), ('foo', 'a')]

type_checking
^^^^^^^^^^^^^
Runtime type checking with support for import paths and type hints.

.. code:: python

    >>> from tippo import Mapping
    >>> from itertools import chain
    >>> from basicco.type_checking import is_instance
    >>> class SubChain(chain):
    ...     pass
    ...
    >>> is_instance(3, int)
    True
    >>> is_instance(3, (chain, int))
    True
    >>> is_instance(3, ())
    False
    >>> is_instance(SubChain(), "itertools.chain")
    True
    >>> is_instance(chain(), "itertools.chain", subtypes=False)
    True
    >>> is_instance(SubChain(), "itertools.chain", subtypes=False)
    False
    >>> is_instance({"a": 1, "b": 2}, Mapping[str, int])
    True

unique_iterator
^^^^^^^^^^^^^^^
Iterator that yields unique values.

.. code:: python

    >>> from basicco.unique_iterator import unique_iterator
    >>> list(unique_iterator([1, 2, 3, 3, 4, 4, 5]))
    [1, 2, 3, 4, 5]

weak_reference
^^^^^^^^^^^^^^
Weak Reference-like object that supports pickling.