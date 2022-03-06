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

# N.B. could instead be "from networkx import DiGraph"
# networkx.classes used to make mypy happy

import ast
import logging
from typing import Any, Optional

import click
import rich
from beartype import beartype
from networkx.classes.digraph import DiGraph
from pyvis.network import Network
from rich.progress import Progress
import rich_click

from depythel import __version__
from depythel_api.depythel._utility_imports import AnyTree
from depythel_api.depythel.main import tree_generator, topological_sort

log = logging.getLogger(__name__)


# From https://github.com/ewels/rich-click#the-good-and-proper-way
# Used for formatting click help output with rich
class RichClickGroup(click.Group):
    def format_help(self, ctx, formatter):
        rich_click.rich_format_help(self, ctx, formatter)


class RichClickCommand(click.Command):
    def format_help(self, ctx, formatter):
        rich_click.rich_format_help(self, ctx, formatter)


@click.group(cls=RichClickGroup)
@click.version_option(__version__)
def depythel() -> None:
    """Interdependency Visualiser and Dependency Hell scrutiniser."""


# TODO: Allow passing in a json file containing the tree
# TODO: Figure out how to allow double quotes on the outside
class TreeType(click.ParamType):
    """Parses the user's tree from the command line.

    e.g. Turns an input of '{"a": "b", "b": "a"}' into {"a": "b", "b": "a"}

    Based on https://click.palletsprojects.com/en/8.0.x/parameters/#implementing-custom-types
    """

    name = "tree"

    @beartype
    def convert(
        self,
        value: str,
        param: Optional[click.core.Parameter],
        ctx: Optional[click.core.Context],
    ) -> Any:
        """Parses the user's string into a dictionary, and errors out if it's not possible."""
        try:
            return ast.literal_eval(value)
        # TODO: Check if other errors can be raised
        except ValueError:
            self.fail(
                f"{value} is an invalid tree.",
                param,
                ctx,
            )


TREE_TYPE = TreeType()


@beartype
def support_pipe(
    ctx: Optional[click.core.Context], param: Optional[click.core.Parameter], value: Any
) -> Any:
    """This allows the depythel function to support piping input."""
    # Based on https://github.com/pallets/click/issues/1370#issuecomment-522549260
    if not value and not click.get_text_stream("stdin").isatty():
        # Piped input (and maybe stdin input)
        user_input = click.get_text_stream("stdin").read().strip()
        if param is not None and param.human_readable_name == "TREE":
            return TREE_TYPE.convert(user_input, None, None)
        return user_input
    # No input provided
    # TODO: Are there other ways to reach this?
    return value


# TODO: Improve optional dependency management
@click.argument("tree", callback=support_pipe, required=False, type=TREE_TYPE)
@click.argument(
    "path",
    type=click.Path(dir_okay=False, writable=True),
)
@depythel.command(cls=RichClickCommand)
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
@depythel.command(cls=RichClickCommand)
@beartype
def topological(tree: AnyTree) -> None:
    topological_sort(tree)


# TODO: Figure out how to deal with invalid project name.
# Might be better to deal with at the API level first.
# click.secho("👀 Cannot find project", fg="red", err=True)
@click.argument("number", type=int)
@click.argument("repository")
@click.argument("name")
@depythel.command(cls=RichClickCommand)
@beartype
def generate(name: str, repository: str, number: int) -> None:
    """Outputs a dependency tree in JSON format.

    A tree is generated for NAME from REPOSITORY. It generates NUMBER amounts of children.

    """
    generator = tree_generator(name, repository)
    with Progress(transient=True) as progress:
        task = progress.add_task("🧪 Processing...", total=100)
        for _ in range(number):
            final_tree = generator()
            progress.update(task, advance=100 / number)
    # Unlike API, output in a visual format
    rich.print_json(data=final_tree)
