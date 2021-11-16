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
compatibility issues and feature gaps between Python 2.7 and Python 3.7+.

So I decided to implement solutions for those issues at the `Base`_, literally.

Overview
--------
`Basicco` provides a `Base`_ class and multiple lower-level `Utilities`_ that enhance
code compatibility, readability, and validation.

Base
----
The `Base`_ class enables functionalities provided by `Basicco`.
It is designed to be a simple drop-in replacement for `object` when defining your base
classes:

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
    AttributeError: 'Asset' instance is frozen, can't set attribute

If you wish to freeze a class without freezing its subclasses or to freeze an instance
at any point in time, you can use the `freeze` function instead:

.. code:: python

    >>> from basicco import Base, freeze
    >>> class Asset(Base):
    ...     typename = "geometry"
    ...
    >>> Asset.typename = "nurbs"  # this works, since the class is not frozen yet
    >>> freeze(Asset)  # will freeze the class (not its subclasses)
    >>> Asset.typename = "joint"
    Traceback (most recent call last):
    AttributeError: class 'Asset' is frozen, can't set class attribute

.. code:: python

    >>> from basicco import Base, freeze
    >>> class Asset(Base):
    ...     def __init__(self, name, typename):
    ...         self.name = name
    ...         self.typename = typename
    ...
    >>> asset = Asset("cube", "geometry")
    >>> asset.name = "sphere"  # this works, since the instance is not frozen yet
    >>> freeze(asset)
    >>> asset.name = "cone"
    Traceback (most recent call last):
    AttributeError: 'Asset' instance is frozen, can't set attribute

final
^^^^^
Runtime-checked version of the
`typing.final <https://docs.python.org/3/library/typing.html#typing.final>`_ decorator.

Can be used directly on methods but also on properties, classmethods, and staticmethods
(even in Python 2.7).

This decorator is still recognized by Mypy static type checking, and it also prevents
subclassing and/or member overriding during runtime:

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
    <__main__.Asset.Config object at...>

generic
^^^^^^^
Better support for the `typing.Generic` class (even in Python 2.7).

In Python 2.7 (without using `Basicco`) the example below would give you True due to a
bug in the `typing` module. The `Base`_ fixes that bug.

.. code:: python

    >>> from typing import Generic, TypeVar
    >>> from basicco import Base
    >>> T = TypeVar("T")
    >>> class Asset(Base, Generic[T]):
    ...     pass
    ...
    >>> Asset[int] != Asset[int,]
    False

Utilities
---------

caller_module
^^^^^^^^^^^^^
Retrieve the caller's module name.

.. code:: python

    >>> from basicco.utils.caller_module import get_caller_module
    >>> def do_something():
    ...     caller_module = get_caller_module()
    ...     return "I was called by {}".format(caller_module)
    ...
    >>> do_something()
    'I was called by __main__'

custom_repr
^^^^^^^^^^^
Custom representation functions.

.. code:: python

    >>> from basicco.utils.custom_repr import custom_mapping_repr
    >>> dct = {"a": 1, "b": 2}
    >>> custom_mapping_repr(
    ...     dct, prefix="<", suffix=">", template="{key}={value}", sorting=True
    ... )
    "<'a'=1, 'b'=2>"

.. code:: python

    >>> from basicco.utils.custom_repr import custom_iterable_repr
    >>> tup = ("a", "b", "c", 1, 2, 3)
    >>> custom_iterable_repr(tup, prefix="<", suffix=">", value_repr=str)
    '<a, b, c, 1, 2, 3>'

dummy_context
^^^^^^^^^^^^^
Dummy (no-op) context manager.

.. code:: python

    >>> from threading import RLock
    >>> from basicco.utils.dummy_context import dummy_context
    >>> lock = RLock()
    >>> def do_something(thread_safe=True):
    ...     with lock if thread_safe else dummy_context():
    ...         print("did something")
    ...
    >>> do_something(thread_safe=False)
    did something

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
Python 2.7 compatible way to find the qualified name inspired by
`wbolster/qualname <https://github.com/wbolster/qualname>`_.

.. code:: python

    >>> from basicco.utils.qualified_name import get_qualified_name
    >>> class Asset(object):
    ...     class Config(object):
    ...         pass
    ...
    >>> get_qualified_name(Asset.Config)
    'Asset.Config'

reducer
^^^^^^^
Python 2.7 compatible reducer method that works with qualified name and slots.

.. code:: python

    >>> import pickle
    >>> from basicco.utils.reducer import reducer
    >>> class Asset(object):
    ...     class Config(object):
    ...         __reduce__ = reducer  # reducer method
    ...         __slots__ = ("name", "version")
    ...         def __init__(self):
    ...             self.name = "cube"
    ...             self.version = 2
    ...
    >>> pickled = pickle.dumps(Asset.Config())
    >>> pickle.loads(pickled)
    <__main__.Asset.Config object at...>

state
^^^^^
Utility functions for managing an object's state.

.. code:: python

    >>> from basicco.utils.state import get_state, update_state
    >>> class SlottedObject(object):
    ...     __slots__ = ("a", "b")
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    ...
    >>> slotted_obj = SlottedObject(1, 2)
    >>> obj_state = get_state(slotted_obj)
    >>> obj_state["a"], obj_state["b"]
    (1, 2)
    >>> update_state(slotted_obj, {"a": 3, "b": 4})
    >>> obj_state = get_state(slotted_obj)
    >>> obj_state["a"], obj_state["b"]
    (3, 4)

type_checking
^^^^^^^^^^^^^
Runtime type checking with support for import paths.

.. code:: python

    >>> from itertools import chain
    >>> from basicco.utils.type_checking import is_instance

    >>> class SubChain(chain):
    ...     pass
    ...
    >>> is_instance(3, int)
    True
    >>> is_instance(3, (chain, int))
    True
    >>> is_instance(3, ())
    False
    >>> is_instance(SubChain(), "itertools|chain")
    True
    >>> is_instance(chain(), "itertools|chain", subtypes=False)
    True
    >>> is_instance(SubChain(), "itertools|chain", subtypes=False)
    False

.. code:: python

    >>> from itertools import chain
    >>> from basicco.utils.type_checking import is_subclass

    >>> class SubChain(chain):
    ...     pass
    ...
    >>> is_subclass(int, int)
    True
    >>> is_subclass(int, (chain, int))
    True
    >>> is_subclass(int, ())
    False
    >>> is_subclass(SubChain, "itertools|chain")
    True
    >>> is_subclass(chain, "itertools|chain", subtypes=False)
    True
    >>> is_subclass(SubChain, "itertools|chain", subtypes=False)
    False

.. code:: python

    >>> from itertools import chain
    >>> from basicco.utils.type_checking import assert_is_instance

    >>> class SubChain(chain):
    ...     pass
    ...
    >>> assert_is_instance(3, int)
    >>> assert_is_instance(3, (chain, int))
    >>> assert_is_instance(3, ())
    Traceback (most recent call last):
    ValueError: no types were provided to perform assertion
    >>> assert_is_instance(3, "itertools|chain")
    Traceback (most recent call last):
    TypeError: got 'int' object, expected instance of 'chain' or any of its subclasses
    >>> assert_is_instance(chain(), "itertools|chain", subtypes=False)
    >>> assert_is_instance(SubChain(), "itertools|chain", subtypes=False)
    Traceback (most recent call last):
    TypeError: got 'SubChain' object, expected instance of 'chain' (instances of subclasses are not accepted)

.. code:: python

    >>> from itertools import chain
    >>> from basicco.utils.type_checking import assert_is_subclass

    >>> class SubChain(chain):
    ...     pass
    ...
    >>> assert_is_subclass(int, int)
    >>> assert_is_subclass(int, (chain, int))
    >>> assert_is_subclass(int, ())
    Traceback (most recent call last):
    ValueError: no types were provided to perform assertion
    >>> assert_is_subclass(int, "itertools|chain")
    Traceback (most recent call last):
    TypeError: got 'int', expected class 'chain' or any of its subclasses
    >>> assert_is_subclass(chain, "itertools|chain", subtypes=False)
    >>> assert_is_subclass(SubChain, "itertools|chain", subtypes=False)
    Traceback (most recent call last):
    TypeError: got 'SubChain', expected class 'chain' (subclasses are not accepted)

.. code:: python

    >>> from basicco.utils.type_checking import assert_is_subclass

    >>> assert_is_callable(int)
    >>> assert_is_callable(lambda: None)
    >>> assert_is_callable(3)
    Traceback (most recent call last):
    TypeError: got non-callable 'int' object, expected a callable

weak_reference
^^^^^^^^^^^^^^
Weak reference-like object that supports pickling.

.. code:: python

    >>> import pickle
    >>> from basicco.utils.weak_reference import WeakReference
    >>> class MyClass(object):
    ...     pass
    ...
    >>> strong = MyClass()
    >>> weak = WeakReference(strong)
    >>> pickle.loads(pickle.dumps((strong, weak)))
    (<__main__.MyClass object at...>, <WeakReference object at...; to 'MyClass' at...>)
