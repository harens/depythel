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

"""Retrieves dependencies from Homebrew, a macOS package manager."""

import json
from urllib.request import urlopen

from depythel._utility_imports import CacheType, DictType


# pylint doesn't like the dicttype return type.
# TODO: might be nice to have the dictionary quotations be double quotes
# This allows compatibility with JSON
@CacheType
def online(
    name: str,
) -> DictType[str, str]:  # pylint: disable=unsubscriptable-object
    """Retrieves dependencies for NAME from the Homebrew API.

    Information is fetched from https://formulae.brew.sh/api/formula/NAME.json.

    Each dependency is grouped into the following categories:

    - build_dependencies
    - dependencies (required at build and runtime)
    - optional_dependencies
    - recommended_dependencies

    Args:
       name: The name of the formula to retrieve the dependencies for.

    Returns: A dictionary of build/run/etc. dependencies.

    Examples:
        >>> from depythel.api.repository.homebrew import online
        >>> online("folderify")
        {'imagemagick': 'dependencies', 'python@3.9': 'dependencies'}
        >>> online("gping")
        {'rust': 'build_dependencies'}
        >>> online("pkg-config")
        {}
    """
    with urlopen(f"https://formulae.brew.sh/api/formula/{name}.json") as api_response:
        json_response = json.load(api_response)

    return {
        dep: category
        for category in (
            "dependencies",
            "recommended_dependencies",
            "optional_dependencies",
            "build_dependencies",
        )
        for dep in json_response[category]
    }
