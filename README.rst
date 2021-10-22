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

`Basicco` provides base metaclasses and utility functions that enhance compatibility and
validation across multiple versions of Python.

Motivation
----------
`Basicco` tries to address some of the lower-level issues that I've encountered while
working on code for Visual Effects pipelines.

Because of the need for maintaining compatibility all the way back to Python 2.7 (which
has reached end-of-life but is still widely in use), I sometimes found myself stuck
between writing code that looks more modern and that works with many Python versions.

`Basicco` offers features to bridge that gap a little bit. Some of the solutions are
really a stop-gap, which is not very glamorous, but do make for better and safer code,
especially in an environment where test coverage can be low and things like static type
checking are a luxury and far from being fully implemented.

Base
----
The `Base`_ class combines all the functionalities provided by `Basicco` into a single
access point. In most of the cases, it's a drop-in replacement for `object`.
