#!/usr/bin/env python3

# Copyright (c) 2021, harens
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
from collections import deque
from typing import Any, Callable, Optional, Union

from depythel._typing_imports import DictType

# Standard tree e.g. {'a': 'b', 'b': 'a'}
# A descriptive tree might show dependency type e.g. runtime/build
StandardTree = DictType[str, str]  # pylint: disable=unsubscriptable-object
DescriptiveTree = DictType[str, DictType[str, str]]  # pylint: disable=unsubscriptable-object
AnyTree = Union[StandardTree, DescriptiveTree]


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
'clang-13': 'build', 'curl': 'lib', 'zlib': 'lib', 'openssl11': 'lib', \
'libgit2': 'lib', 'libssh2': 'lib', 'rust': 'lib'}}
    """
    tree = {}
    stack = deque([name])

    try:
        module = importlib.import_module(f"depythel.api.repository.{repository}")
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            f"{repository} is not a supported repository"
        ) from error

    # Recommends not to use hasattr: https://hynek.me/articles/hasattr/
    # Instead, set a default attribute as none, and check whether it exists
    module_attribute = getattr(module, "online", None)

    # This hopefully shouldn't happen, but just in case the online module doesn't exist
    if module_attribute is None:
        # TODO: Maybe make this error messaging better
        raise AttributeError(
            f"{repository} does not support retrieving dependencies from online"
        )

    def get_next_child() -> AnyTree:
        nonlocal stack, tree
        # pop turns this into depth first (via a stack)
        # popleft turns it info breadth first (via a queue)
        next_child = stack.popleft()
        # We've checked to make sure that the attribute is defined
        children = module.online(next_child)  # type: ignore[attr-defined]
        tree[next_child] = children
        stack.extend((child for child in children if child not in deque(tree) + stack))
        return tree

    return get_next_child


def retrieve_from_stack(variable: str) -> Optional[Any]:
    """Private function to retrieve a local variable from the recursion stack.

    This means that it doesn't have to be passed as an argument.
    Based on https://stackoverflow.com/a/58598665

    Args:
        variable: The variable whose value should be achieved.

    Returns:
        The value of the variable.

    Examples:
        >>> from depythel.api.main import retrieve_from_stack
        >>> a = 2
        >>> def demo():
        ...     a = 1
        ...     return retrieve_from_stack('a')
        >>> demo()
        1
        >>> retrieve_from_stack('a')
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
        pkgconfig --> clang-9.0 --> pkgconfig
        pkgconfig --> clang-9.0 --> cmake --> clang-9.0
        pkgconfig --> clang-9.0 --> cctools --> clang-9.0
        pkgconfig --> libiconv --> clang-9.0 --> pkgconfig
        pkgconfig --> libiconv --> clang-9.0 --> cmake --> clang-9.0
        pkgconfig --> libiconv --> clang-9.0 --> cctools --> clang-9.0
        Unfinished children in tree: bzip2, clang_select, curl, expat, gperf, ld64, libarchive, \
libcxx, libomp, libunwind-headers, libuv, libxml2, llvm-10, llvm-9.0, ncurses, perl5, xz, zlib
        True
    """
    return_value = False
    start_call = False

    exploring = retrieve_from_stack("exploring")
    unfinished = retrieve_from_stack("unfinished")

    # If the exploring list isn't defined, add the root node
    # Else, add the current child to the exploring list
    if isinstance(exploring, deque):
        # TODO: Maybe check that the deque is specifically a string?
        # Could take the beartype approach of checking a random/first element
        exploring.append(root)
    else:
        exploring = deque([root])

    # TODO: Refactor of this type checking
    if not isinstance(unfinished, set):
        # If the variables are undefined, we are starting for the first time.
        start_call = True
        unfinished = set()

    children = (child for child in tree[root])

    for child in children:
        if child in exploring:
            # TODO: Provide some opinionated way of determining which cycles are worse.
            # TODO: Highlight dependency that is circular
            # Since this is the api, maybe don't use arrows
            print(" --> ".join(exploring + deque([child])))
            if first:
                return True
            return_value = True
        # Be careful of leaves, where they have no children i.e. empty dict?
        elif isinstance(child, str):
            if child not in tree:
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
        print(f"Unfinished children in tree: {', '.join(sorted(unfinished))}")
    return return_value
