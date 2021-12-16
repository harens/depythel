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

"""Tests retrieving dependencies from the MacPorts repository"""

import pytest
from pytest_mock import MockFixture

from depythel.api.repository.macports import online


def test_standard_response(session_mocker: MockFixture) -> None:
    """Standard Expected 200 response."""

    session_mocker.patch("depythel.api.repository.macports.urlopen")
    session_mocker.patch(
        "depythel.api.repository.macports.json.load",
        return_value={
            "name": "gping",
            "portdir": "net/gping",
            "version": "1.2.3",
            "license": "MIT",
            "platforms": "darwin",
            "epoch": 0,
            "replaced_by": None,
            "homepage": "https://github.com/orf/gping",
            "description": "ping, but with a graph",
            "long_description": "ping, but with a graph.",
            "active": True,
            "categories": ["net"],
            "maintainers": [{"name": "harens", "github": "harens", "ports_count": 11}],
            "variants": ["universal"],
            "dependencies": [{"type": "build", "ports": ["cargo", "clang-12"]}],
            "depends_on": [],
        },
    )
    assert online("gping") == {"cargo": "build", "clang-12": "build"}
