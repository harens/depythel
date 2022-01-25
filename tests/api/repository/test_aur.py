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

"""Tests retrieving dependencies from the AUR"""

from urllib.error import HTTPError

import pytest
from pytest_mock import MockFixture

from depythel.api.repository.aur import online


def test_standard_response(session_mocker: MockFixture) -> None:
    """Standard Expected 200 response."""

    session_mocker.patch("depythel.api.repository.aur.urlopen")
    session_mocker.patch(
        "depythel.api.repository.aur.json.load",
        return_value={
            "version": 5,
            "type": "multiinfo",
            "resultcount": 1,
            "results": [
                {
                    "ID": 1020332,
                    "Name": "python39",
                    "PackageBaseID": 173933,
                    "PackageBase": "python39",
                    "Version": "3.9.10-1",
                    "Description": "Major release 3.9 of the Python high-level programming language",
                    "URL": "https://www.python.org/",
                    "NumVotes": 10,
                    "Popularity": 5.880225,
                    "OutOfDate": None,
                    "Maintainer": "rixx",
                    "FirstSubmitted": 1639396599,
                    "LastModified": 1642471216,
                    "URLPath": "/cgit/aur.git/snapshot/python39.tar.gz",
                    "Depends": [
                        "bzip2",
                        "expat",
                        "gdbm",
                        "libffi",
                        "libnsl",
                        "libxcrypt",
                        "openssl",
                        "zlib",
                    ],
                    "MakeDepends": ["bluez-libs", "mpdecimal", "gdb"],
                    "OptDepends": ["sqlite", "mpdecimal", "xz", "tk"],
                    "Provides": ["python=3.9.10"],
                    "License": ["custom"],
                    "Keywords": [],
                }
            ],
        },
    )
    assert online("python39") == {
        "bzip2": "Depends",
        "expat": "Depends",
        "gdbm": "Depends",
        "libffi": "Depends",
        "libnsl": "Depends",
        "libxcrypt": "Depends",
        "openssl": "Depends",
        "zlib": "Depends",
        "bluez-libs": "MakeDepends",
        "mpdecimal": "OptDepends",
        "gdb": "MakeDepends",
        "sqlite": "OptDepends",
        "xz": "OptDepends",
        "tk": "OptDepends",
    }


def test_invalid_response(session_mocker: MockFixture) -> None:
    """If the user's input isn't a valid project in the AUR."""
    session_mocker.patch(
        "depythel.api.repository.aur.json.load",
        return_value={
            "version": 5,
            "type": "multiinfo",
            "resultcount": 0,
            "results": [],
        },
    )
    with pytest.raises(HTTPError):
        online("idontexist")
