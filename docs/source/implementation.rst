Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Logging
--------

.. 
    TODO: WOULD BE NICE TO GET EXAMPLE OUTPUT OF LOGGING

Logging is an important part of the debugging process. It can reduce the time taken to spot bugs, and it helps developers
have a better understanding of how data is parsed by their modules. To that end, depythel takes the approach of having
a levelled logging system.

Within each Python file, a logger is setup based on the name of the module it is in.

.. code-block:: python

    import logging

    log = logging.getLogger(__name__)

This allows the loggers of individual modules to be configured separately. As part of having a levelled logging system, there
are three different types of logs.

+---------+----------------------------------------------------+----------------------------------+
| Level   | Purpose                                            | Visible to clients in ``stdout`` |
+=========+====================================================+==================================+
| DEBUG   | Default level. Used to check correct functionality | No                               |
+---------+----------------------------------------------------+----------------------------------+
| WARNING | Used when a cycle is detected                      | Yes                              |
+---------+----------------------------------------------------+----------------------------------+
| ERROR   | If something goes wrong                            | Yes                              |
+---------+----------------------------------------------------+----------------------------------+

By default, debug logs are not outputted to the user and have to be manually enabled. This allows for them to be enabled
only during development and not in the final release. Error and warning logs are always outputted to the user.

.. code-block:: python

    def _tree_generator(self) -> Callable[[], AnyTree]:
        ...
        try:
            module = importlib.import_module(f"depythel.repository.{self.repo}")
            log.debug(f"Using functions from depythel.repository.{self.repo}")
        except ModuleNotFoundError:
            log.error(f"{self.repo} is not a supported repository", exc_info=True)
            raise
        ...

In the above code, determining which online repository to fetch from is sent to debug. This is since it is a normal
and expected routine, and there are no errors.

If the user enters a repository that doesn't exist, this is an error and so is logged accordingly.

Supporting Python 3.7+
------------------------

One of the aims that depythel set out to do was to work on all supported Python versions, which at the time of writng,
is Python 3.7-3.10. The main difficulty of this are the type hints, especially with supporting pre-3.9. Python 3.9 introduced
a new notation of writing type hints in a more native fashion.

.. code-block:: python

    # Old method of writing type hints
    # pre-Python 3.9

    from typing import List

    def example() -> List[str]:
        return ['a', 'b', 'c']

    # New Method
    # Python 3.9+

    # No need to import from typing
    def example() -> list(str):
        return ['a', 'b', 'c']

Obviously, the new style could not be used pre-Python 3.9 since it would not be recognised.

The natural solution to this would be to use the old method everywhere, since it is still supported. Although it looks less neat, especially
when lots of classes are being imported from ``typing``, the functionality would still be the same.

However, the introduction of `PEP 585 <https://www.python.org/dev/peps/pep-0585>`_ meant that the old notation would break in
around 2025/2026 with some new Python version [1]_. In the unlikely (but possible) scenario where depythel is still around, this
would mean it would fail to run on the latest version of Python.

The solution to this is to conditionally use the new notation in any Python 3.9+, and the old notation pre-3.9.

.. [1] Curry, C., 2022. beartype/README.rst at main · beartype/beartype. [online] GitHub. Available at: <https://github.com/beartype/beartype#what-does-this-mean> [Accessed 22 March 2022].

.. code-block:: python

    # Extended from https://github.com/beartype/beartype#are-we-on-the-worst-timeline

    import sys
    from typing import Union

    if sys.version_info >= (3, 9):  # pragma: no cover
        from collections import deque
        from collections.abc import Generator
        from functools import cache

        CacheType = cache
        DequeType = deque
        DictType = dict
        GeneratorType = Generator
        ListType = list
        SetType = set
    else:  # pragma: no cover
        from functools import lru_cache
        from typing import Deque, Dict, Generator, List, Set

        CacheType = lru_cache(maxsize=None)
        DequeType = Deque
        DictType = Dict
        GeneratorType = Generator
        ListType = List
        SetType = Set

These typing hints are then stored in a `_utility_imports` file, which can then be imported by the entire code base.

.. code-block:: python

    # ListType becomes list on 3.9+
    # ...and becomes typing.List pre-3.9

    from depythel._utility_imports import ListType

    def example() -> ListType[str]:
        return ['a', 'b', 'c']

For the command line tool, we have the benefit of being allowed to use third-party dependencies. As such, ``beartype`` provides
a module similar to `_utility_imports` that conditionally provides the right type hints.

.. code-block:: python

    # Similar to above, this can either be typing.List or list

    from beartype.typing import List

    def example() -> List[str]:
        return ['a', 'b', 'c']

Using ``beartype.typing`` in the command line tool has a few benefits.

- No need to import from a private module in the API, which would be bad practice since the API and CLT are different packages.
- ``beartype.typing`` will be more throughly tested.
- It just works as expected.

Tree Types
***********

In a similar fashion to the variable type hints, we can also define custom type aliases for the different types of trees that are supported
and import them when required.

.. table::
    :widths: 9 41

    +------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Tree type        | Purpose                                                                                                                                                                                              |
    +==================+======================================================================================================================================================================================================+
    | StandardTree     | The most basic tree that only shows one dependency of a project. As an example A → B → C would be represented as ``{"A": "B", "B": "C"}``.                                                           |
    +------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | DescriptiveTree  | A more powerful tree that can store multiple dependencies for a project and its purpose. If A requires B as a build dependency, and C as a library dependency: ``{"A": {"B": "build", "C": "lib"}}`` |
    +------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | AnyTree          | Either a StandardTree or a DescriptiveTree                                                                                                                                                           |
    +------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

These can be defined in ``_utility_imports``, so that they can be imported anywhere within the code base.

.. code-block:: python

    # Standard tree e.g. {'a': 'b', 'b': 'a'}
    # A descriptive tree might show dependency type e.g. runtime/build
    StandardTree = DictType[str, str]  # pylint: disable=unsubscriptable-object
    DescriptiveTree = DictType[
        str, DictType[str, str]
    ]  # pylint: disable=unsubscriptable-object
    AnyTree = Union[StandardTree, DescriptiveTree]

.. code-block:: python

    from depythel._utility_imports import StandardTree

    def fetch_tree() -> StandardTree:
        """Returns a tree where a depends on b, and b depends on c."""
        return {'a': 'b', 'b': 'c'}
