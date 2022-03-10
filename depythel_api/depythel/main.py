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
# TODO: Allow for other repositories (not just MacPorts)
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


# Use https://www.diffchecker.com/diff for checking doctests
def tree_generator(name: str, repository: str) -> Callable[[], AnyTree]:
    """Generate a dependency tree via level-order traversal.

    Each call of the generator builds the next child in the tree.

    Args:
        name: The name of the project for which a dependency tree will be generated.
        repository: The package manager to retrieve information from.

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
    tree: AnyTree = {}  # type: ignore[assignment]
    stack = deque([name])

    try:
        module = importlib.import_module(f"depythel.repository.{repository}")
        log.debug(f"Using functions from depythel.repository.{repository}")
    except ModuleNotFoundError:
        log.error(f"{repository} is not a supported repository", exc_info=True)
        raise

    # Recommends not to use hasattr: https://hynek.me/articles/hasattr/
    # Instead, set a default attribute as none, and check whether it exists
    module_attribute = getattr(module, "online", None)

    # This hopefully shouldn't happen, but just in case the online module doesn't exist
    if module_attribute is None:
        # TODO: Maybe make this error messaging better
        log.error(f"{repository} does not support retrieving dependencies from online")
        raise AttributeError(
            f"{repository} does not support retrieving dependencies from online"
        )

    def get_next_child() -> AnyTree:
        nonlocal stack, tree
        # pop turns this into depth first (via a stack)
        # popleft turns it info breadth first (via a queue)
        if not stack:
            log.debug("No more children left in stack - finished")
            return tree
        next_child = stack.popleft()
        log.debug(f"Retrieving dependencies for {next_child} - popped from stack")
        # We've checked to make sure that the attribute is defined
        children = module.online(next_child)
        log.debug(f"{next_child}'s dependencies: {children.keys()}")
        tree[next_child] = children
        stack.extend((child for child in children if child not in deque(tree) + stack))
        log.debug(f"Adding {next_child}'s dependencies to the stack")
        return tree

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


# TODO: Why does this detect more cycles than the original method?
# TODO: This can hit the recursion limit!!!
def cycle_check(root: str, tree: AnyTree, first: bool = False) -> bool:
    """Perform a level-order traversal of an adjacency list looking for any cycles.

    Args:
        root: The root node of the dependency tree.
        tree: The dependency tree to traverse in the form of an adjacency list.
        first: If true, the function halts as soon as the first cycle is found.
            Otherwise, it traverses the whole tree looking for every cycle.

    Returns:
        A boolean representing whether a cycle has been detected or not.

    Examples:
        >>> from depythel.api.main import tree_generator, cycle_check
        >>> pkgconfig_generator = tree_generator('pkgconfig', 'macports')
        >>> # Generate 5 children in the tree
        >>> for children in range(5):
        ...     tree = pkgconfig_generator()
        >>> cycle_check('pkgconfig', tree)
        True
    """
    return_value = False
    start_call = False

    exploring = _retrieve_from_stack("exploring")
    unfinished = _retrieve_from_stack("unfinished")

    # If the exploring list isn't defined, add the root node
    # Else, add the current child to the exploring list
    if isinstance(exploring, deque):
        # TODO: Maybe check that the deque is specifically a string?
        # Could take the beartype approach of checking a random/first element
        exploring.append(root)
    else:
        log.debug("Initialising exploring stack")
        exploring = deque([root])

    log.debug(f"Added {root} to exploring stack")

    # TODO: Refactor of this type checking
    if not isinstance(unfinished, set):
        # If the variables are undefined, we are starting for the first time.
        log.debug("Assuming first recursive call of cycle_check")
        start_call = True
        unfinished = set()
        log.debug("Initialised unfinished set")  # TODO: What is the unfinished set?

    children = (child for child in tree[root])

    for child in children:
        if child in exploring:
            # TODO: Provide some opinionated way of determining which cycles are worse.
            # TODO: Highlight dependency that is circular
            # Since this is the api, maybe don't use arrows
            log.info(" --> ".join(exploring + deque([child])))
            if first:
                return True
            return_value = True
        elif child not in tree:
            # Maybe give some confidence interval based on no./type of cycles
            # and completeness of graph
            unfinished.add(child)
        else:
            if cycle_check(child, tree, first):
                if first:
                    return True
                return_value = True

    # For some reason, this remove is necessary. TODO: Find out why
    # e.g. traversing 2 level first of py-beartype
    exploring.remove(root)

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


# TODO: Examples
def all_items(tree: AnyTree) -> SetType[str]:
    """Generates all the projects in a dependency tree.

    Args:
        tree: The dependency tree to traverse in the form of an adjacency list.

    Returns:
        A set of strings representing all the projects in the tree.

    Examples:
        >>> from depythel.api.main import all_items
        >>> # a --> b --> c
        >>> all_items({"a": "b", "b": "c"})
        {'a', 'b', 'c'}
        >>> # No dependencies
        >>> all_items({"gping": {}})
        {'gping'}
    """
    all_items_list: DequeType[str] = deque()
    # Assumes the graph is connected, which it should be since it's a tree
    # If it's a standard tree (check the first item)
    if isinstance(tuple(tree.values())[0], str):
        tree = cast(StandardTree, tree)
        # Add all keys and values from dictionary
        all_items_list.extend(tree.values())
    else:  # If it's a descriptive tree
        tree = cast(DescriptiveTree, tree)
        for dep in tree.values():
            all_items_list.extend(tuple(dep.keys()))

    root_project = tuple(tree)[0]
    # If cycle with root project present, it will already be in the list
    if root_project not in all_items_list:
        all_items_list.append(root_project)
    # Use set to remove duplicates
    return set(all_items_list)


def depends_on(project: str, tree: AnyTree) -> GeneratorType[str, None, None]:
    """Determines items in a tree that depend on a given project.

    Args:
        project: A string representing a project in the tree
        tree: An adjacency list tree which contains the given project.

    Returns:
        A generator for all the items that depend on the given project.

    Examples:
        >>> from depythel.api.main import depends_on
        >>> # Depends on b in the tree a --> b --> c
        >>> list(depends_on("b", {"a": "b", "b": "c"}))
        ['a']
    """
    return (item for item in tree if project in tree[item])


# See https://courses.cs.washington.edu/courses/cse326/03wi/lectures/RaoLect20.pdf page 7
# in degree is the number of times it appears in tuple(tuple(i.keys()) for i in tree.values())
def topological_sort(tree: AnyTree) -> DequeType[str]:
    """Determines an order in which dependencies can be installed.

    Args:
        tree: A directed acyclic graph representing a dependency tree.

    Returns:
        A deque representing a possible topological sorting of the tree. Raises
            StopIteration if no ordering is possible.

    Examples:
        >>> from depythel.api.main import topological_sort
        >>> topological_sort({"A": "B", "B": "C"})
        deque(['C', 'B', 'A'])
    """
    all_projects = all_items(tree)

    # Dictionary storing projects and how many dependencies they have.
    dep_count: DictType[str, int] = {}

    for item in all_projects:
        try:
            dep_count[item] = len(tree[item])
            log.debug(f"{item} dependency count set to {len(tree[item])}")
        except KeyError:
            log.warning(f"{item} dependency count set to 0 - not present in tree")
            dep_count[item] = 0

    final_ordering: DequeType[str] = deque()
    while dep_count:
        try:
            # Choose item if it has no dependencies
            to_remove = next(item for item in dep_count if dep_count[item] == 0)
            log.debug(f"{to_remove} next item in ordering")
        except StopIteration:
            log.error(f"Cycle present - No topological ordering present", exc_info=True)
            raise
        final_ordering.append(to_remove)
        # Decrement dep count of dependents of to_remove
        for item in depends_on(to_remove, tree):
            dep_count[item] -= 1
            log.debug(f"Decrementing {item} dep count to {dep_count[item]}")
        log.debug(f"Finished with {to_remove}")
        del dep_count[to_remove]  # Remove item from count

    return final_ordering
