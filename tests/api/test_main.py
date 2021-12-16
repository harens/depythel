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

"""Tests functions related to generating the dependency tree."""

from typing import Any, Optional

import pytest
from pytest_mock import MockFixture

from depythel.api.main import cycle_check, retrieve_from_stack, tree_generator


class TestTreeGenerator:
    def test_standard_response(self, session_mocker: MockFixture) -> None:
        """Standard project."""
        session_mocker.patch(
            "depythel.api.repository.macports.online",
            return_value={"cargo": "build", "clang-12": "build"},
        )
        gping_generator = tree_generator("gping", "macports")
        assert gping_generator() == {"gping": {"clang-12": "build", "cargo": "build"}}

    def test_invalid_repository(self) -> None:
        """Errors out if the repository isn't supported."""
        with pytest.raises(ModuleNotFoundError):
            tree_generator("gping", "I_dont_exist")

    def test_no_online_support(self, session_mocker: MockFixture) -> None:
        """If, for whatever reason, online support isn't available."""
        # TODO: Test if the return value is none if the online module doesn't exist.
        session_mocker.patch("depythel.api.main.getattr", return_value=None)
        with pytest.raises(AttributeError):
            # The repo has to exist to pass the invalid repo test first.
            tree_generator("gping", "macports")


def test_retrieve_from_stack() -> None:
    """Test retrieving the contents of variables from the stack."""
    ### Test Program
    a = 2

    def demo() -> Optional[Any]:
        a = 1
        return retrieve_from_stack("a")

    ###

    assert demo() == 1
    assert retrieve_from_stack("a") == 2
    assert retrieve_from_stack("doesnt-exist") == None


class TestCycleCheck:
    def test_standard_cycle(self) -> None:
        """Simple cycle a --> b and b --> a"""
        assert cycle_check("a", {"a": "b", "b": "a"})

    def test_first_cycle(self) -> None:
        """Returns true as soon as the first cycle is found."""
        assert cycle_check("a", {"a": "b", "b": "a"}, True)

    def test_no_cycle(self) -> None:
        """Simple no cycles present."""
        assert not cycle_check("a", {"a": "b", "b": "c"})
