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

"""Retrieves dependencies from the AUR, the Arch Linux User Repository."""

import json
from urllib.error import HTTPError
from urllib.request import urlopen

from depythel._utility_imports import CacheType, DictType

# TODO: sort out errors where packages don't exist
# e.g. expat should be expat-git


# pylint doesn't like the dicttype return type.
# TODO: might be nice to have the dictionary quotations be double quotes
# This allows compatability with JSON
@CacheType
def online(
    name: str,
) -> DictType[str, str]:  # pylint: disable=unsubscriptable-object
    """Retrieves dependencies for NAME from the AUR web RPC interface.

    Information is fetched from https://aur.archlinux.org/rpc/?v=5&type=info&arg[]=NAME

    Each dependency is grouped into the following categories:

    - Depends
    - MakeDepends
    - OptDepends
    - CheckDepends

    Args:
       name: The name of the project to retrieve the dependencies for.

    Returns: A dictionary of build/run/etc. dependencies.

    Examples:
        >>> from depythel.api.repository.aur import online
        >>> online("rget")
        {'rustup': 'MakeDepends'}
        >>> online("gmp-hg")
        {'gcc-libs': 'Depends', 'sh': 'Depends', 'mercurial': 'MakeDepends'}
        >>> online("anaconda")
        {}
    """
    url = f"https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={name}"
    with urlopen(url) as api_response:
        json_response = json.load(api_response)

    if json_response["resultcount"] == 0:
        raise HTTPError(url, 404, "Not Found", api_response.info(), None)

    return {
        dep: category
        for category in (
            "Depends",
            "MakeDepends",
            "OptDepends",
            "CheckDepends",
        )
        for dep in json_response["results"][0].get(category, [])
    }
