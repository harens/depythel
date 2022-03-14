#!/usr/bin/env python3

# Copyright (c) 2021-2022, Haren Samarasinghe
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of seaport nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Generates and traverses dependency tress of various projects."""

# TODO: Sort out if online, if offline
# TODO: Test docstrings
# TODO: At some point, refactor off the module checking
# TODO: When retrieving from stack, make sure the variable isn't one with the same name
# set by the user
# TODO: Remove print statements - This is meant to be an api

import importlib
import inspect
import logging
from collections import deque
from typing import Any, Callable, Optional, cast

from depythel._utility_imports import (
    AnyTree,
    DequeType,
    DescriptiveTree,
    DictType,
    GeneratorType,
    SetType,
    StandardTree,
)

log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

# TODO: Implement defensive programming
# TODO: Deal with None in standard tree
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

        # Mypy doesn't seem to like the casting, whilst pycharm does like it
        # pycharm says all is good, so ignore the mypy errors
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

    # TODO: Why does this detect more cycles than the original method?
    # TODO: This can hit the recursion limit!!!
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
        start_call = False

        exploring = _retrieve_from_stack("exploring")
        unfinished = _retrieve_from_stack("unfinished")
        current_project = _retrieve_from_stack("current_project")

        # TODO: Refactor of this type checking
        if not isinstance(unfinished, set):
            # If the variables are undefined, we are starting for the first time.
            log.debug("Assuming first recursive call of cycle_check")
            start_call = True
            unfinished = set()
            log.debug("Initialised unfinished set")  # TODO: What is the unfinished set?

        current_project = (
            current_project if isinstance(current_project, str) else self.root
        )
        backup_current_project = current_project  # Backup of the current project in case it's modified below.
        log.debug(f"Current project is {current_project}")

        # If the exploring list isn't defined, add the current_project node
        # Else, add the current child to the exploring list
        if isinstance(exploring, deque):
            # TODO: Maybe check that the deque is specifically a string?
            # Could take the beartype approach of checking a random/first element
            exploring.append(current_project)
        else:
            log.debug("Initialising exploring stack")
            exploring = deque([current_project])
        log.debug(f"Added {current_project} to exploring stack")

        children = (child for child in self.tree[current_project])

        for child in children:
            if child in exploring:
                # TODO: Provide some opinionated way of determining which cycles are worse.
                # TODO: Highlight dependency that is circular
                # Since this is the api, maybe don't use arrows
                log.warning(" --> ".join(exploring + deque([child])))
                if first:
                    return True
                return_value = True
            elif child not in self.tree:
                # Maybe give some confidence interval based on no./type of cycles
                # and completeness of graph
                unfinished.add(child)
            else:
                current_project = child
                if self.cycle_check(first):
                    if first:
                        return True
                    return_value = True

        # For some reason, this remove is necessary. TODO: Find out why
        # e.g. traversing 2 level first of py-beartype
        exploring.remove(backup_current_project)
        log.debug(f"Removing {backup_current_project} from exploring stack.")

        # Only return unfinished children in the first recursive call
        if start_call and len(unfinished) > 0:
            # TODO: Printing in an API is generally not great
            # Maybe return it or add it to warning log?
            # Sorted for reproducibility of tests
            # See https://github.com/PyCQA/pylint/issues/1788#issuecomment-410381475
            log.info(
                f"Unfinished children in tree: {', '.join(sorted(unfinished))}"
            )  # pylint: disable=logging-fstring-interpolation
        return return_value


class Tree(LocalTree):
    """Manages a dependency tree from an online repository."""

    def __init__(self, root: str, repository: str, size: int = 1):
        """Manages a dependency tree from an online repository.

        Args:
            root: The project whose dependency tree should be fetched.
            repository: Where to fetch information about a project from.
            size: The number of projects that should be in the tree. Defaults to
                1 during initialisation.
        """
        self.root = root
        """str: The root of the dependency tree"""

        self.repo = repository
        """str: Where information about the repository is being fetched from."""

        self.size = size
        """int: The number of projects in the tree. Defaults to 1 during initialisation"""

        # For some reason, mypy doesn't like the type alias
        # However, the dictionary always remains a dictionary
        self.tree: AnyTree = {}  # type: ignore[assignment]
        """AnyTree: An adjacency list representing a dependency tree."""

        self.generator = self._tree_generator()
        """Callable[[], AnyTree]: Generates dependencies for a project from the specified repository."""
        self.set_size(self.size)

        super(Tree, self).__init__(self.tree)

    # TODO: In testing, have grow then shrink then grow
    def set_size(self, new_size: int) -> None:
        """Set the number of dependencies that should be present in the tree.

        Args:
            new_size: How many projects there should be in the dependency tree.

        >>> from depythel.main import Tree
        >>> example = Tree('gping', 'macports')
        >>> example.tree
        {'gping': {'cargo': 'build', 'clang-13': 'build'}}
        >>> example.set_size(2)
        >>> example.tree
        {'gping': {'cargo': 'build', 'clang-12': 'build'}, \
    'cargo': {'cargo-bootstrap': 'build', 'cmake': 'build', 'pkgconfig': 'build', \
    'clang-12': 'build', 'curl': 'lib', 'zlib': 'lib', 'openssl11': 'lib', \
    'libgit2': 'lib', 'libssh2': 'lib', 'rust': 'lib'}}
        """
        if new_size < 1:
            raise AttributeError("Size must be greater or equal to 1")

        # If new items need to be added or the tree hasn't been initiated yet.
        while len(self.tree) < new_size:
            # Pass the tree by value, such that del below doesn't affect if.
            new_tree = self.generator().copy()
            if new_tree == self.tree:
                # If there are no more children in the fetched tree from the repo, break.
                break
            self.tree = new_tree
            log.debug(f"Increasing - Tree items: {tuple(self.tree)}")
        log.debug("Finished increasing tree")
        # Shrink the tree if required.
        # After the first while loop, the tree might be bigger than expected.
        # e.g. if grow followed by shrink then grow, the generator is larger than expected.
        while len(self.tree) > new_size:
            log.debug(f"Removing {tuple(self.tree)[-1]}")
            del self.tree[tuple(self.tree)[-1]]
        self.size = new_size

    # Use https://www.diffchecker.com/diff for checking doctests
    def _tree_generator(self) -> Callable[[], AnyTree]:
        """Generate a dependency tree via level-order traversal.

        Each call of the generator builds the next child in the tree.

        Returns:
            An adjacency list representing the generated part of a dependency tree.

        Examples:
            >>> from depythel.api.main import tree_generator
            >>> # Creates a generator for the gping project from the MacPorts repository
            >>> gping_generator = tree_generator('gping', 'macports')
            >>> gping_generator()
            {'gping': {'cargo': 'build', 'clang-12': 'build'}}
            >>> gping_generator()
            {'gping': {'cargo': 'build', 'clang-12': 'build'}, \
    'cargo': {'cargo-bootstrap': 'build', 'cmake': 'build', 'pkgconfig': 'build', \
    'clang-12': 'build', 'curl': 'lib', 'zlib': 'lib', 'openssl11': 'lib', \
    'libgit2': 'lib', 'libssh2': 'lib', 'rust': 'lib'}}
        """
        # For some reason, mypy doesn't like the type alias
        # However, the dictionary always remains a dictionary
        generated_tree: AnyTree = {}  # type: ignore[assignment]
        stack = deque([self.root])

        try:
            module = importlib.import_module(f"depythel.repository.{self.repo}")
            log.debug(f"Using functions from depythel.repository.{self.repo}")
        except ModuleNotFoundError:
            log.error(f"{self.repo} is not a supported repository", exc_info=True)
            raise

        # Recommends not to use hasattr: https://hynek.me/articles/hasattr/
        # Instead, set a default attribute as none, and check whether it exists
        module_attribute = getattr(module, "online", None)

        # This hopefully shouldn't happen, but just in case the online module doesn't exist
        if module_attribute is None:
            # TODO: Maybe make this error messaging better
            log.error(
                f"{self.repo} does not support retrieving dependencies from online"
            )
            raise AttributeError(
                f"{self.repo} does not support retrieving dependencies from online"
            )

        def get_next_child() -> AnyTree:
            nonlocal stack, generated_tree
            # pop turns this into depth first (via a stack)
            # popleft turns it info breadth first (via a queue)
            if not stack:
                log.debug("No more children left in stack - finished")
                return generated_tree
            next_child = stack.popleft()
            log.info(f"Retrieving dependencies for {next_child} - popped from stack")
            # We've checked to make sure that the attribute is defined
            children = module.online(next_child)
            log.debug(f"{next_child}'s dependencies: {tuple(children)}")
            generated_tree[next_child] = children
            stack.extend(
                (
                    child
                    for child in children
                    if child not in deque(generated_tree) + stack
                )
            )
            log.debug(f"Adding {next_child}'s dependencies to the stack")
            return generated_tree

        return get_next_child


def _retrieve_from_stack(variable: str) -> Optional[Any]:
    """Private function to retrieve a local variable from the recursion stack.

    This means that it doesn't have to be passed as an argument.
    Based on https://stackoverflow.com/a/58598665

    Args:
        variable: The variable whose value should be achieved.

    Returns:
        The value of the variable.

    Examples:
        >>> from depythel.api.main import _retrieve_from_stack
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
