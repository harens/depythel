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

"""Retrieves dependencies for a port in the online MacPorts registry."""

# TODO: How to speed up fetch request?

import json
from urllib.request import urlopen

from depythel._typing_imports import CacheType, DictType


# pylint doesn't like the dicttype return type.
@CacheType
def online(portname: str) -> DictType[str, str]:  # pylint: disable=unsubscriptable-object
    """Retrieve the dependencies of a port from the MacPorts website.

    This is done via the Django Rest API. e.g. https://ports.macports.org/api/v1/ports/wget/, and
    includes all the deps (build/runtime/test/etc.)

    Args:
       portname: The name of the port to retrieve the dependencies for.

    Returns: A dictionary of build/run/etc. dependencies.

    Examples:
        >>> from depythel.api.repository.macports import online
        >>> online('gping')
        {'cargo': 'build', 'clang-12': 'build'}
        >>> online('py39-checkdigit')
        {'clang-9.0': 'build', 'py39-setuptools': 'build', 'python39': 'lib'}
    """
    # The slash at the end is required, otherwise some ports return a 404
    # response = requests.get(f"https://ports.macports.org/api/v1/ports/{portname}/")

    # TODO: Maybe deal with HTTPError more nicely
    with urlopen(f"https://ports.macports.org/api/v1/ports/{portname}/") as api_response:
        # Convert the HTTP request into standard JSON
        json_response = json.load(api_response)

    # return {item["type"]: item["ports"] for item in response.json()["dependencies"]}
    # "is not None" check since in rare occasions the result is null
    # e.g. https://ports.macports.org/port/libgcc11/details/ for runtime dep
    # TODO: What happens if a project has no dependencies?
    return {
        dep: item["type"]
        for item in json_response["dependencies"]
        for dep in item["ports"]
        if dep is not None
    }
