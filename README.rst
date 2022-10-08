.. logo_start
.. raw:: html

   <p align="center">
     <a href="https://github.com/brunonicko/basicco">
         <picture>
            <object data="./_static/basicco.svg" type="image/png">
                <source srcset="./docs/source/_static/basicco_white.svg" media="(prefers-color-scheme: dark)">
                <img src="./docs/source/_static/basicco.svg" width="60%" alt="basicco" />
            </object>
         </picture>
     </a>
   </p>
.. logo_end

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

Overview
--------
`basicco` is a Python package that provides low-level `Base Classes`_ and `Utilities`_ to enhance code compatibility,
features and validation.

Motivation
----------
While developing Python software for Visual Effects pipelines, I found myself having to write the same boiler-plate
code over and over again, as well as struggling with compatibility issues and feature gaps between Python 2.7 and
Python 3.7+.

So I decided to implement solutions for those issues at the `Base`_, and `basicco` was born.

Base Classes
------------

CompatBase
^^^^^^^^^^
The goal with the `CompatBaseMeta` metaclass and the `CompatBase` class is to bridge some of the feature gaps between
Python 2.7 and Python 3.7+.

This includes adding Python 2.7 workarounds for:
  - `Abstract properties <https://docs.python.org/3/library/abc.html#abc.abstractproperty>`_: Better `abstractmethod`
    decorator support for property-like descriptors. See also `abstract_class`_.
  - `PEP 487 <https://peps.python.org/pep-0487/>`_: Support for `__init_subclass__` and `__set_name__`.
    See also `init_subclass`_ and `set_name`_.
  - `object.__dir__ <https://docs.python.org/3/reference/datamodel.html#object.__dir__>`_: Base `__dir__` method.
    See also `default_dir`_.
  - `__eq__ override <https://docs.python.org/3/reference/datamodel.html#object.__hash__>`_: Overriding `__eq__` will
    set `__hash__` to None. See also `implicit_hash`_.
  - `PEP 307 <https://peps.python.org/pep-0307/>`_: Support for pickling objects with `__slots__`.
    See also `obj_state`_.
  - `PEP 3155 <https://peps.python.org/pep-03155/>`_: Qualified name `__qualname__` for nested classes.
    See also `qualname`_.
  - `__ne__ behavior <https://docs.python.org/3.0/whatsnew/3.0.html#operators-and-special-methods>`_: By default,
    `__ne__` should negate the result of `__eq__`.
    See also `safe_not_equals`_
  - `PEP 0560 <https://peps.python.org/pep-0560/>`_: Better handling of Generic classes.
    See also `tippo <https://github.com/brunonicko/tippo#generic-fixes>`_.

Base
^^^^
In addition to the compatibility solutions, the goal with the `BaseMeta` metaclass and the `Base` class is to add
useful low-level features that hopefully yield better code readability and validation.

This includes:
  - `__weakref__` slot: Added by default.
  - `locked_class`_: Public class attributes are read-only by default.
  - `explicit_hash`_: Overriding `__eq__` without overriding `__hash__` will raise an error.
  - `namespace`_: Adds a protected `__namespace` unique to each class.
  - `runtime_final`_: Runtime checking for classes and methods decorated with `final`.

SlottedBase
^^^^^^^^^^^
The `SlottedBase` class and the `SlottedBaseMeta` metaclass offer all features from `Base` and `BaseMeta` plus implicit
`__slots__` declaration. See `slotted <https://github.com/brunonicko/slotted>`_ for more information.

Utilities
---------
Apart from the features integrated into the base classes, `basicco` provides a variety of general utilities.
Those can be imported from the sub-modules described below.

abstract_class
^^^^^^^^^^^^^^
Better `abstract classes <https://docs.python.org/3/library/abc.html#abc.abstractmethod>`_ support.

Provides abstract decorators that can be used directly on methods but also on classes, properties, classmethods, and
staticmethods (even in Python 2.7).

.. code:: python

    >>> from six import with_metaclass
    >>> from basicco.abstract_class import AbstractMeta, abstract
    >>> class Asset(with_metaclass(AbstractMeta, object)):
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

    >>> from basicco.abstract_class import AbstractMeta, abstract
    >>> @abstract
    ... class Asset(with_metaclass(AbstractMeta, object)):
    ...     pass
    ...
    >>> Asset()
    Traceback (most recent call last):
    TypeError: can't instantiate abstract class 'Asset'

basic_data
^^^^^^^^^^
Eases the task of creating simple data container classes that support equality comparisons, hashing, string
representation, conversion to dictionary, etc.

.. code:: python

    >>> from math import sqrt
    >>> from basicco.basic_data import ItemUsecase, BasicData
    >>> class Vector(BasicData):
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...     def to_items(self, usecase=None):
    ...         items = [("x", self.x), ("y", self.y)]
    ...         if usecase is ItemUsecase.REPR:
    ...             items.append(("mag", self.mag))
    ...         return items
    ...     @property
    ...     def mag(self):
    ...         return sqrt(self.x**2 + self.y**2)
    ...
    >>> Vector(3.0, 4.0)
    Vector(x=3.0, y=4.0, <mag=5.0>)

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
Backport of the `contextvars` module for Python 2.7, based on
`MagicStack/contextvars <https://github.com/MagicStack/contextvars>`_.

When imported from Python 3, it redirects the contents to the native
`contextvars <https://docs.python.org/3/library/contextvars.html>`_ module.

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
Custom representation functions for mappings, items, and iterables.

.. code:: python

    >>> from basicco.custom_repr import mapping_repr
    >>> dct = {"a": 1, "b": 2}
    >>> mapping_repr(dct, prefix="<", suffix=">", template="{key}={value}", sorting=True)
    "<'a'=1, 'b'=2>"

.. code:: python

    >>> from basicco.custom_repr import mapping_repr
    >>> items = [("a", 1), ("b", 2)]
    >>> mapping_repr(items, prefix="[", suffix="]", template=lambda i, key, value: key + " -> " + value)
    "['a' -> 1, 'b' -> 2]"

.. code:: python

    >>> from basicco.custom_repr import iterable_repr
    >>> tup = ("a", "b", "c", 1, 2, 3)
    >>> iterable_repr(tup, prefix="<", suffix=">", value_repr=str)
    '<a, b, c, 1, 2, 3>'

default_dir
^^^^^^^^^^^
Backport of Python 3's implementation of
`object.__dir__ <https://docs.python.org/3/reference/datamodel.html#object.__dir__>`_ for Python 2.7.

This allows for calling `super().__dir__()` from a subclass to leverage the default implementation.

.. code:: python

    >>> from six import with_metaclass
    >>> from basicco.default_dir import DefaultDir
    >>> class Class(DefaultDir):
    ...     def __dir__(self):
    ...         return super(Class, self).__dir__()
    ...
    >>> obj = Class()
    >>> dir(obj)
    [...]

dynamic_code
^^^^^^^^^^^^
Generate debuggable code on the fly that supports line numbers on tracebacks.

.. code:: python

    >>> from basicco.dynamic_code import make_function, generate_unique_filename
    >>> class MyClass(object):
    ...     pass
    ...
    >>> bar = 'bar'
    >>> # Prepare the script and necessary data.
    >>> script = "\n".join(
    ...     (
    ...         "def __init__(self):",
    ...         "    self.foo = 'bar'",
    ...     )
    ... )
    >>> # Gather information.
    >>> name = "__init__"
    >>> owner_name = MyClass.__name__
    >>> module = MyClass.__module__
    >>> filename = generate_unique_filename(name, module, owner_name)
    >>> globs = {"bar": bar}
    >>> # Make function and attach it as a method.
    >>> MyClass.__init__ = make_function(name, script, globs, filename, module)
    >>> obj = MyClass()
    >>> obj.foo
    'bar'

explicit_hash
^^^^^^^^^^^^^
Metaclass that forces `__hash__` to be declared whenever `__eq__` is declared.

.. code:: python

    >>> from six import with_metaclass
    >>> from basicco.explicit_hash import ExplicitHashMeta
    >>> class Asset(with_metaclass(ExplicitHashMeta, object)):
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
    >>> fabricate_value(None, 3)  # no factory, value passthrough
    3
    >>> fabricate_value(str, 3)  # callable factory
    '3'
    >>> fabricate_value("str", 3)  # use an import path
    '3'
    >>> fabricate_value(int)  # no input value, just the factory itself
    0

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

hash_cache_wrapper
^^^^^^^^^^^^^^^^^^
An integer subclass that pickles/copies as None. This can be used to avoid serializing a cached hash value.

.. code:: python

    >>> from copy import copy
    >>> from basicco.hash_cache_wrapper import HashCacheWrapper
    >>> hash_cache = HashCacheWrapper(12345)
    >>> print(hash_cache)
    12345
    >>> print(copy(hash_cache))
    None

implicit_hash
^^^^^^^^^^^^^
Metaclass that forces `__hash__` to None when `__eq__` is declared.
This is a backport of the default behavior in Python 3.

.. code:: python

    >>> from six import with_metaclass
    >>> from basicco.implicit_hash import ImplicitHashMeta
    >>> class Asset(with_metaclass(ImplicitHashMeta, object)):
    ...     def __eq__(self, other):
    ...         pass
    ...
    >>> Asset.__hash__ is None
    True

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
This works for both Python 2 (using `__kwargs__`) and 3 (using the new class parameters).

.. code:: python

    >>> from basicco.init_subclass import InitSubclass
    >>> class Foo(InitSubclass):
    ...     def __init_subclass__(cls, foo=None, **kwargs):
    ...         cls.foo = foo
    ...
    >>> class Bar(Foo):
    ...     __kwargs__ = {"foo": "bar"}  # you can specify cls kwargs on py2 like this
    ...
    >>> Bar.foo
    'bar'

locked_class
^^^^^^^^^^^^^
Prevents changing public class attributes.

.. code:: python

    >>> from six import with_metaclass
    >>> from basicco.locked_class import LockedClassMeta
    >>> class Foo(with_metaclass(LockedClassMeta, object)):
    ...     pass
    ...
    >>> Foo.bar = "bar"
    Traceback (most recent call last):
    AttributeError: can't set read-only class attribute 'bar'

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

Also provides a `NamespacedMeta` metaclass that adds a `__namespace` protected class attribute that is unique to each
class.

.. code:: python

    >>> from six import with_metaclass
    >>> from basicco.namespace import NamespacedMeta
    >>> class Asset(with_metaclass(NamespacedMeta, object)):
    ...     @classmethod
    ...     def set_class_value(cls, value):
    ...         cls.__namespace.value = value
    ...
    ...     @classmethod
    ...     def get_class_value(cls):
    ...         return cls.__namespace.value
    ...
    >>> Asset.set_class_value("foobar")
    >>> Asset.get_class_value()
    'foobar'

obj_state
^^^^^^^^^
Get/update the state of an object, slotted or not (works even in Python 2.7).

.. code:: python

    >>> from basicco.obj_state import get_state
    >>> class Slotted(object):
    ...     __slots__ = ("foo", "bar")
    ...     def __init__(self, foo, bar):
    ...         self.foo = foo
    ...         self.bar = bar
    ...
    >>> slotted = Slotted("a", "b")
    >>> sorted(get_state(slotted).items())
    [('bar', 'b'), ('foo', 'a')]

Also provides a `ReducibleMeta` metaclass that allows for pickling instances of slotted classes in Python 2.7.

qualname
^^^^^^^^
Python 2.7 compatible way of getting the qualified name. Based on
`wbolster/qualname <https://github.com/wbolster/qualname>`_.
Also provides a `QualnamedMeta` metaclass with a `__qualname__` class property for Python 2.7.

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

Can be used on methods, properties, classmethods, staticmethods, and classes that have `RuntimeFinalMeta` as a metaclass.
It is also recognized by static type checkers and prevents subclassing and/or member overriding during runtime:

.. code:: python

    >>> from six import with_metaclass
    >>> from basicco.runtime_final import RuntimeFinalMeta, final
    >>> @final
    ... class Asset(with_metaclass(RuntimeFinalMeta, object)):
    ...     pass
    ...
    >>> class SubAsset(Asset):
    ...     pass
    ...
    Traceback (most recent call last):
    TypeError: can't subclass final class 'Asset'

.. code:: python

    >>> from six import with_metaclass
    >>> from basicco.runtime_final import RuntimeFinalMeta, final
    >>> class Asset(with_metaclass(RuntimeFinalMeta, object)):
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

    >>> from six import with_metaclass
    >>> from basicco.runtime_final import RuntimeFinalMeta, final
    >>> class Asset(with_metaclass(RuntimeFinalMeta, object)):
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

safe_not_equals
^^^^^^^^^^^^^^^
Backport of the default Python 3 behavior of `__ne__` behavior for Python 2.7.

.. code:: python

    >>> from six import with_metaclass
    >>> from basicco.safe_not_equals import SafeNotEqualsMeta
    >>> class Class(with_metaclass(SafeNotEqualsMeta, object)):
    ...     pass
    ...
    >>> obj_a = Class()
    >>> obj_b = Class()
    >>> assert (obj_a == obj_a) is not (obj_a != obj_a)
    >>> assert (obj_b == obj_b) is not (obj_b != obj_b)
    >>> assert (obj_a == obj_b) is not (obj_a != obj_b)

safe_repr
^^^^^^^^^
Decorator that prevents `__repr__` methods from raising exceptions and return a default representation instead.

.. code:: python

    >>> from basicco.safe_repr import safe_repr
    >>> class Class(object):
    ...     @safe_repr
    ...     def __repr__(self):
    ...         raise RuntimeError("oh oh")
    ...
    >>> obj = Class()
    >>> repr(obj)
    "<__main__.Class object at ...; repr failed due to 'RuntimeError: oh oh'>"

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