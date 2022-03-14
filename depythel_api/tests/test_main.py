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

"""Tests functions related to generating the dependency tree."""

from collections import deque
from typing import Any, Optional

import pytest
from pytest_mock import MockFixture

from depythel.main import LocalTree, Tree, _retrieve_from_stack


class TestSetSize:
    def test_invalid_grow(self, session_mocker: MockFixture) -> None:
        """Test entering an invalid size for the dependency tree."""
        session_mocker.patch(
            "depythel.repository.macports.online",
            return_value={"cargo": "build", "clang-12": "build"},
        )
        gping_tree = Tree("gping", "macports")
        with pytest.raises(AttributeError):
            gping_tree.set_size(-1)

    def test_no_children(self, session_mocker: MockFixture) -> None:
        """If the user tries to grow a tree with no dependencies."""
        session_mocker.patch(
            "depythel.repository.homebrew.online",
            return_value={},
        )
        pkg_config_tree = Tree("pkg-config", "homebrew")
        pkg_config_tree.set_size(3)
        assert pkg_config_tree.tree == {"pkg-config": {}}
        pkg_config_tree.set_size(2)
        assert pkg_config_tree.tree == {"pkg-config": {}}

    def test_grow_shrink(self, session_mocker: MockFixture) -> None:
        """Grow a tree and then shrink it."""
        session_mocker.patch(
            "depythel.repository.homebrew.online",
            side_effect=(
                {"rust": "build_dependencies"},
                {"libssh2": "dependencies", "openssl@1.1": "dependencies"},
            ),
        )

        gping_tree = Tree("gping", "homebrew")
        gping_tree.set_size(2)
        assert gping_tree.tree == {
            "gping": {"rust": "build_dependencies"},
            "rust": {"libssh2": "dependencies", "openssl@1.1": "dependencies"},
        }
        gping_tree.set_size(1)
        assert gping_tree.tree == {"gping": {"rust": "build_dependencies"}}


class TestTreeGenerator:
    def test_standard_response(self) -> None:
        """Standard project."""
        gping_tree = Tree("gping", "macports")
        # Uses mocker from above
        assert gping_tree.generator()["gping"] == {
            "cargo": "build",
            "clang-12": "build",
        }

    def test_invalid_repository(self) -> None:
        """Errors out if the repository isn't supported."""
        with pytest.raises(ModuleNotFoundError):
            gping_tree = Tree("gping", "I_dont_exist")

    def test_no_deps(self, session_mocker: MockFixture) -> None:
        """If the project contains no dependencies."""
        session_mocker.patch(
            "depythel.repository.homebrew.online",
            return_value={},
        )
        pkg_config_tree = Tree("pkg-config", "homebrew")

        # After two runs, the function should check the children
        # and realise there aren't any.
        assert pkg_config_tree.generator() == {"pkg-config": {}}
        assert pkg_config_tree.generator() == {"pkg-config": {}}

    def test_no_online_support(self, session_mocker: MockFixture) -> None:
        """If, for whatever reason, online support isn't available."""
        # TODO: Test if the return value is none if the online module doesn't exist.
        session_mocker.patch("depythel.main.getattr", return_value=None)
        with pytest.raises(AttributeError):
            # The repo has to exist to pass the invalid repo test first.
            gping_tree = Tree("gping", "macports")


def test_retrieve_from_stack() -> None:
    """Test retrieving the contents of variables from the stack."""
    # Test Program
    a = 2

    def demo() -> Optional[Any]:
        a = 1
        return _retrieve_from_stack("a")

    #

    assert demo() == 1
    assert _retrieve_from_stack("a") == 2
    assert _retrieve_from_stack("doesnt-exist") is None


class TestCycleCheck:
    def test_standard_cycle(self) -> None:
        """Simple cycle a --> b and b --> a"""
        cycle_present = LocalTree({"a": "b", "b": "a"})
        assert cycle_present.cycle_check()

    def test_all_cycle(self) -> None:
        """Returns true after all cycles are found"""
        cycle_present = LocalTree({"a": "b", "b": "a"})
        assert cycle_present.cycle_check(False)

    def test_no_cycle(self) -> None:
        """Simple no cycles present."""
        no_cycles = LocalTree({"a": "b", "b": "c"})
        assert not no_cycles.cycle_check()


# N.B. Topological sorting isn't necessarily reproducible.
# This is since there can be many valid solutions.
# Testcases should be used with only one possible solution to reflect this.
class TestTopologicalSort:
    def test_simple_standard(self) -> None:
        """Standard non-descriptive tree."""
        test_tree = LocalTree({"a": "b", "b": "c"})
        assert test_tree.topological_sort() == deque(["c", "b", "a"])

    def test_unfinished_descriptive(self) -> None:
        """Descriptive tree that isn't complete."""
        # c doesn't have a definition.
        test_tree = LocalTree({"a": {"b": "hi", "c": "bye"}, "b": {"c": "hello"}})
        assert test_tree.topological_sort() == deque(["c", "b", "a"])

    def test_cycle(self) -> None:
        """Tree that contains cycle => Topological sorting not possible."""
        test_tree = LocalTree({"a": "b", "b": "a"})
        with pytest.raises(StopIteration):
            test_tree.topological_sort()
