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

Application Programming Interface
-----------------------------------

As discussed in the :ref:`Design`, two separate classes were to be created to allow users to manage
their dependencies more effectively. One aimed to support pre-defined dependency trees defined by
an online repo. The other was to support custom user-defined trees.

Local Tree
***********

The local tree class supports dependency trees generated by the user in the form of a dictionary.

.. code-block:: python

    >>> from depythel.main import LocalTree
    >>> # A depends on B, which depends on A
    >>> example_tree = LocalTree({"A": "B", "B": "A"})
    >>> example_tree.cycle_check()
    True

As part of this process, the following methods were implemented.

Initialisation
_______________

Firstly, based on the user's input, the tree has to be set up accordingly via an ``__init__`` function.

.. code-block:: python

    class LocalTree:
        """A tree class to manage a dependency tree for a specified adjacency list."""

        def __init__(self, tree: AnyTree) -> None:
            """A tree class to manage a dependency tree for a specified adjacency list.

            Args:
                tree: An adjacency list representing a dependency tree.

            Examples:
                >>> from depythel.main import LocalTree
                >>> # A depends on B, and B depends on C
                >>> example1 = LocalTree({"A": "B", "B": "C"})
                >>> # A depends on B (library dependency) and C (build dependency)
                >>> # B requires C to build, and C doesn't require anything.
                >>> example2 = LocalTree({"A": {"B": "lib", "C": "build"}, "B": {"C": "build"}, "C": {}})
            """
            self.tree = tree
            """AnyTree: An adjacency list representing a dependency tree."""

            self.root = tuple(self.tree)[0]
            """str: The root of the dependency tree."""

            self._standard_tree: bool = False
            """bool: Whether the tree inputted is a standard tree or a descriptive tree."""

            # Assumes the graph is connected, which it should be since it's a tree
            # Checks the first item to determine the tree type
            if isinstance(tuple(self.tree.values())[0], str):
                self.tree = cast(StandardTree, self.tree)
                self._standard_tree = True
            else:
                self.tree = cast(DescriptiveTree, self.tree)

To see how this works, let's run through the generating process with an example.

.. code-block:: python

    >>> from depythel.main import LocalTree
    >>> # A simple tree where A → B → C
    >>> example_tree = LocalTree({"a": "b", "b": "c"})

    >>> # Outputs the current state of the tree.
    >>> example_tree.tree
    {'a': 'b', 'b': 'c'}

    >>> # Determines the root of the provided dependency tree
    >>> example_tree.root
    'a'

    >>> # Whether the tree is a simplo, standard tree or a more complex tree
    >>> example_tree._standard_tree
    True

These attributes are all used by the various methods to help complete their tasks. The final part of the
initialisation is used for determining the correct type hint. It "casts" the right type hint
on the tree attribute depending on what type of tree the user has entered.

All items
___________

Determining all items that are present in the tree is not only a useful function for clients, but is
also used by other modules in the tree class.

.. code-block:: python

    >>> from depythel.main import LocalTree
    >>> example_tree = LocalTree({"a": "b", "b": "c"})
    >>> example_tree.all_items()
    {'a', 'b', 'c'}

    >>> example_tree = LocalTree({"a": {"b": "build", "c": "library"}, "b": {"c": "build"}})
    >>> example_tree.all_items()
    {'a', 'b', 'c'}

.. code-block:: python

    def all_items(self) -> SetType[str]:
        """Generates all the projects in a dependency tree.

        Returns:
            A set of strings representing all the projects in the tree.

        Examples:
            >>> from depythel.main import LocalTree
            >>> # A depends on B, which depends on C.
            >>> example = LocalTree({'A': 'B', 'B': 'C'})
            >>> example.all_items()
            {'A', 'B', 'C'}
        """
        all_items_list: DequeType[str] = deque()

        if self._standard_tree:
            # Add all keys and values from dictionary
            all_items_list.extend(self.tree.values())  # type:ignore[arg-type]
        else:  # If it's a descriptive tree
            for dep in self.tree.values():
                all_items_list.extend(tuple(dep.keys()))  # type:ignore[union-attr]

        # If cycle with root project present, it will already be in the list
        if self.root not in all_items_list:
            all_items_list.append(self.root)
        # Use set to remove duplicates
        return set(all_items_list)

If the tree is just a dictionary of strings (standard tree), then there's a built in method for retrieving
all the projects.

Things become slightly more complicated for descriptive trees. We extract each nested dictionary, and retrieve
the keys in each one. However, the root project isn't in a nested dictionary, so that is added at the end.

If there was a cycle in the tree, the root project would already be in a nested dictionary as a dependency.
In this scenario, it doesn't need to be re-added at the end.

Finally, just in case we have any duplicated dependencies, we can remove them using ``set``.

Inverse Dependencies
_____________________

A dependency tree lists what projects depend on what dependencies. Sometimes, it might be useful to reverse this process.
Given a dependency, what projects require it?

.. code-block:: python

    >>> from depythel.main import LocalTree

    >>> example_tree = LocalTree({"a": "b", "b": "c"})
    >>> list(example_tree.depends_on('b'))
    ['a']

    >>> example_tree = LocalTree({"a": {"b": "build", "c": "library"}, "b": {"c": "build"}})
    >>> list(example_tree.depends_on('c'))
    ['a', 'b']

.. code-block:: python

    def depends_on(self, project: str) -> GeneratorType[str, None, None]:
        """Determines items in a tree that depend on a given project.

        Args:
            project: A string representing a project in the tree

        Returns:
            A generator for all the items that depend on the given project.

        Examples:
            >>> from depythel.main import LocalTree
            >>> # A depends on B, which depends on C
            >>> example = LocalTree({'A': 'B', 'B': 'C'})
            >>> list(example.depends_on('B'))
            ['A']
        """
        return (item for item in self.tree if project in self.tree[item])

This very simple one-liner iterates through the tree checking which projects have the input as a dependency.
Similar to the previous funciton, this one is also used by more complex modules in the tree object.

A generator is produced rather than a list so as to be more memory-efficient. The items 

Topological Sorting
_____________________

Topological sorting determines the correct order to install dependencies in a given dependency tree.

.. code-block:: python

    >>> from depythel.main import LocalTree

    >>> example_tree = LocalTree({"a": {"b": "build", "c": "library"}, "b": {"c": "build"}}) 
    >>> example_tree.topological_sort()
    WARNING: c dependency count set to 0 - not present in tree
    deque(['c', 'b', 'a'])

The warning is outputted since the dependencies of c aren't defined in the example tree. The final result is
a deque (double-ended queue).

.. code-block:: python

    # See https://courses.cs.washington.edu/courses/cse326/03wi/lectures/RaoLect20.pdf page 7
    # in degree is the number of times it appears in tuple(tuple(i.keys()) for i in tree.values())
    def topological_sort(self) -> DequeType[str]:
        """Determines an order in which dependencies can be installed.

        Returns:
            A deque representing a possible topological sorting of the tree. Raises
                StopIteration if no ordering is possible.

        Examples:
            >>> from depythel.main import LocalTree
            >>> # A depends on B, which depends on C
            >>> example = LocalTree({'A': 'B', 'B': 'C'})
            >>> example.topological_sort()
            deque(['C', 'B', 'A'])
        """
        all_projects = self.all_items()

        # Dictionary storing projects and how many dependencies they have.
        dep_count: DictType[str, int] = {}

        for item in all_projects:
            try:
                dep_count[item] = len(self.tree[item])
                log.debug(f"{item} dependency count set to {len(self.tree[item])}")
            except KeyError:
                log.warning(f"{item} dependency count set to 0 - not present in tree")
                dep_count[item] = 0

        final_ordering: DequeType[str] = deque()
        while dep_count:
            try:
                # Choose item if it has no dependencies
                to_remove = next(item[0] for item in dep_count.items() if item[1] == 0)
                log.debug(f"{to_remove} next item in ordering")
            except StopIteration:
                log.error(
                    "Cycle present - No topological ordering present", exc_info=True
                )
                raise
            final_ordering.append(to_remove)
            # Decrement dep count of dependents of to_remove
            for item in self.depends_on(to_remove):
                dep_count[item] -= 1
                log.debug(f"Decrementing {item} dep count to {dep_count[item]}")
            log.debug(f"Finished with {to_remove}")
            del dep_count[to_remove]  # Remove item from count

        return final_ordering

This algorithm follows the basic premise described in :ref:`Topological Ordering`. First, we iterate through
all the projects in the dependency and try to determine how many dependencies each of them have.

We initialise the final ordering as a ``deque``, and continually try to remove any projects that don't have
any dependencies. This process is repeated until there are no more dependencies left, and the final ordering is
outputted.

Retrieving from Recursion Stack
_________________________________

Recursive functions work by passing the result of one call as the arguments of the next call. This can be messy
though if more arguments need to be passed. To reduce the number of arguments required, a function was created
to retrieve local variables from the recursion stack.

.. code-block:: python

    >>> from depythel.main import _retrieve_from_stack
    >>> a = 2
    >>> def demo():
    ...     a = 1
    ...     return _retrieve_from_stack('a')
    >>> demo()
    1
    >>> _retrieve_from_stack('a')
    2

.. code-block:: python

    def _retrieve_from_stack(variable: str) -> Optional[Any]:
        """Private function to retrieve a local variable from the recursion stack.

        This means that it doesn't have to be passed as an argument.
        Based on https://stackoverflow.com/a/58598665

        Args:
            variable: The variable whose value should be achieved.

        Returns:
            The value of the variable.

        Examples:
            >>> from depythel.main import _retrieve_from_stack
            >>> a = 2
            >>> def demo():
            ...     a = 1
            ...     return _retrieve_from_stack('a')
            >>> demo()
            1
            >>> _retrieve_from_stack('a')
            2
        """
        frame = inspect.currentframe()
        while frame:
            if variable in frame.f_locals:
                return frame.f_locals[variable]
            frame = frame.f_back

        return None

The function iterates through all the stack frames, checking whether there are any local variables defined. It isn't
part of the Tree class since it doesn't modify or inspect the user's tree. However, it is used as part of cycle checking.
    
This code is based off `the following <https://stackoverflow.com/a/58598665>`_. A modification was made to return ``None``
if the operation was unsuccessful. This can then be tested for to determine whether the recursive function is being called
for the first time or not.

Cycle Checking
_________________

The algorithm from :ref:`Cyclic-Dependency Checking` is implemented by marking nodes as either **visited**
or **exploring**. If an exploring node is "re-explored", that means there's a cycle present.

.. code-block:: python
    
    >>> from depythel.main import LocalTree

    >>> example_tree = LocalTree({"a": "b", "b": "a"})
    >>> example_tree.cycle_check()
    WARNING: a --> b --> a
    True

    >>> example_tree = LocalTree({"a": {"b": "build", "c": "library"}, "b": {"a": "build"}})
    >>> example_tree.cycle_check()
    WARNING: a --> b --> a
    True

.. code-block:: python

    def cycle_check(self, first: bool = True) -> bool:
        """Perform a level-order traversal of an adjacency list looking for any cycles.

        Args:
            first: If true, the function halts as soon as the first cycle is found.
                Otherwise, it traverses the whole tree looking for every cycle.

        Returns:
            A boolean representing whether a cycle has been detected or not.

        Examples:
            >>> from depythel.main import LocalTree
            >>> # A depends on B, which depends on A
            >>> example = LocalTree({'A': 'B', 'B': 'A'})
            >>> example.cycle_check()
            True
        """
        return_value = False
        
        # Whether the recursive function is being called for the first time
        start_call = False

        # Retrieve all of the previous local variables from the recursive stack
        exploring = _retrieve_from_stack("exploring")
        unfinished = _retrieve_from_stack("unfinished")
        current_project = _retrieve_from_stack("current_project")

        if not isinstance(unfinished, set):
            # If the variables are undefined, we are starting for the first time.
            log.debug("Assuming first recursive call of cycle_check")
            start_call = True
            unfinished = set()
            log.debug("Initialised unfinished set")

        # self.root if first recursive call
        # Otherwise, retrieve it from the previous local variables.
        current_project = (
            current_project if isinstance(current_project, str) else self.root
        )
        backup_current_project = current_project  # Backup of the current project in case it's modified below.
        log.debug(f"Current project is {current_project}")

        # If the exploring list isn't defined, add the current_project node
        # Else, add the current child to the exploring list
        if isinstance(exploring, deque):
            exploring.append(current_project)
        else:
            log.debug("Initialising exploring stack")
            exploring = deque([current_project])
        log.debug(f"Added {current_project} to exploring stack")

        children = (child for child in self.tree[current_project])

        for child in children:
            if child in exploring:
                # We've seen this child before, so a cycle is present
                log.warning(" --> ".join(exploring + deque([child])))
                if first:
                    return True
                return_value = True
            elif child not in self.tree:
                # child's dependencies aren't defined in the tree
                unfinished.add(child)
            else:
                current_project = child
                # Recursively repeat the process with the child dependency
                if self.cycle_check(first):
                    if first:
                        return True
                    return_value = True

        # Once the child has been fully explored, remove it from the exploring stack.
        exploring.remove(backup_current_project)
        log.debug(f"Removing {backup_current_project} from exploring stack.")

        # Only return unfinished children in the first recursive call
        if start_call and len(unfinished) > 0:
            # Sorted for reproducibility of tests
            # See https://github.com/PyCQA/pylint/issues/1788#issuecomment-410381475
            log.info(
                f"Unfinished children in tree: {', '.join(sorted(unfinished))}"
            )  # pylint: disable=logging-fstring-interpolation
        return return_value

Firstly, the module checks if it is being called for the first time, or whether it is part of a
recursive call. If it's a recursive call, all the relevant local variables are fetched from the
previous call via the `_retrieve_from_stack` function. If it's the first time, the variables
are defined as normal.

Using a depth-first approach, the children of each project are explored. This process is repeated
until the same child is found again within the same "exploring path", indicating that a cycle is
present.

The default mode is for the function to halt as soon as the first cycle is detected. This is done
to reduce the amount of time taken. However, an option is provided to detect all the cycles present
in a tree. These are then all outputted to the WARNING log.

Online Tree
*************

This tree should fetch information about a project from an online repository.

.. code-block:: python

    >>> from depythel.main import Tree
    >>> example_tree = Tree('gping', 'macports')
    >>> example_tree.tree
    {'gping': {'cargo': 'build', 'clang-13': 'build'}}
