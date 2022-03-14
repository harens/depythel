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

"""The main functionallity behind the depythel CLT."""

# N.B. could instead be "from networkx import DiGraph"
# networkx.classes used to make mypy happy

import logging

import rich
import rich_click as click
from beartype import beartype
from networkx.classes.digraph import DiGraph
from pyvis.network import Network

from depythel import __version__
from depythel._utility_imports import AnyTree
from depythel.main import LocalTree, Tree
from depythel_clt._click_modules import TREE_TYPE, repository_complete, support_pipe

log = logging.getLogger(__name__)


@click.group()
@click.version_option(__version__)
def depythel() -> None:
    """Interdependency Visualiser and Dependency Hell scrutiniser."""


# TODO: Improve optional dependency management
# TODO: Set size of graph to the whole window
@click.argument("tree", callback=support_pipe, required=False, type=TREE_TYPE)
@click.argument(
    "path",
    type=click.Path(dir_okay=False, writable=True),
)
@depythel.command()
@beartype
def visualise(path: str, tree: AnyTree) -> None:
    """Generates an html file visualising a dependency graph.

    TREE is the tree to visualise in the form of an adjacency list/dictionary.

    PATH shows the path to an html file to store the visualisation of the output.
    e.g. /Users/example/Downloads/tree.html
    """
    # Use digraph instead of tree in case of cycles
    graph = DiGraph(tree)

    network = Network(directed=True)
    network.from_nx(graph)

    # Changes to root node
    network.nodes[0]["size"] = 20
    network.nodes[0]["color"] = "#00ff1e"
    # TODO: Different colour depending on how far away from root node
    # example in docs https://pyvis.readthedocs.io/en/latest/tutorial.html

    network.show(path)
    click.launch(path, locate=True)


@click.argument("tree", callback=support_pipe, required=False, type=TREE_TYPE)
@depythel.command()
@beartype
def topological(tree: AnyTree) -> None:
    """Determines an order in which dependencies can be installed.

    TREE is a directed acyclic graph representing a dependency tree.

    """
    tree_object = LocalTree(tree)
    for item in tree_object.topological_sort():
        click.echo(item)


# TODO: Maybe error if cycle present?
@click.argument("tree", callback=support_pipe, required=False, type=TREE_TYPE)
@click.option(
    "--first/--all",
    default=True,
    help="--first halts after the first cycle is found (default). --all generates all cycles.",
)
@depythel.command()
@beartype
def cycle(tree: AnyTree, first: bool) -> None:
    """Perform a level-order traversal of TREE looking for any cycles."""
    tree_object = LocalTree(tree)
    click.echo(tree_object.cycle_check(first))


# TODO: Figure out how to deal with invalid project name.
# Might be better to deal with at the API level first.
# click.secho("👀 Cannot find project", fg="red", err=True)
@click.argument("number", type=int)
@click.argument("repository", shell_complete=repository_complete)
@click.argument("name")
@depythel.command()
@beartype
def generate(name: str, repository: str, number: int) -> None:
    """Outputs a dependency tree in JSON format.

    A tree is generated for NAME from REPOSITORY. It generates NUMBER amounts of children.

    """
    tree_object = Tree(name, repository, number)
    tree_object.set_size(number)  # TODO: Would be nice to get a progress bar.
    # Unlike API, output in a visual format
    rich.print_json(data=tree_object.tree)
