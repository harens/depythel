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

"""General helper functions for managing the Click CLT."""

import ast
import logging
import os.path
import pkgutil
from typing import Any, Optional

import click
from beartype import beartype
from click import Argument, Context

from depythel import repository
from depythel._utility_imports import ListType

log = logging.getLogger(__name__)


@beartype
def repository_complete(
    _ctx: Context, _args: Argument, incomplete: str
) -> ListType[str]:
    """Provides autocomplete for supported repositories."""
    # Based on https://stackoverflow.com/a/1310912
    pkgpath = os.path.dirname(
        repository.__file__
    )  # Path to __init__.py of depythel.repository
    all_options = (name for _, name, _ in pkgutil.iter_modules([pkgpath]))
    return [option for option in all_options if incomplete in option]


# TODO: Allow passing in a json file containing the tree
class TreeType(click.ParamType):
    """Parses the user's tree from the command line.

    e.g. Turns an input of '{"a": "b", "b": "a"}' into {"a": "b", "b": "a"}

    Based on https://click.palletsprojects.com/en/8.0.x/parameters/#implementing-custom-types
    """

    # N.B. This intentionally overrides the standard name attribute and convert method.
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
        except (SyntaxError, ValueError):
            self.fail(
                f"{value} is an invalid tree.",
                param,
                ctx,
            )


TREE_TYPE = TreeType()


@beartype
def support_pipe(
    _ctx: Optional[click.core.Context],
    param: Optional[click.core.Parameter],
    value: Any,
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
