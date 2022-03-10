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

from click.testing import CliRunner
from depythel_clt import __version__
from depythel_clt.main import depythel
import pathlib
import os
from pytest_mock import MockFixture


def test_version() -> None:
    """Simple version number check."""
    runner = CliRunner()
    result = runner.invoke(depythel, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"depythel, version {__version__}\n"


def test_help() -> None:
    """Check the help prompt."""
    runner = CliRunner()
    result = runner.invoke(depythel, ["--help"])
    assert result.exit_code == 0
    assert "Usage: depythel" in result.output


def test_visualise(tmp_path: pathlib.Path, session_mocker: MockFixture) -> None:
    """Checks for the existence of an html file following the visualisation command."""
    runner = CliRunner()

    # Don't show the path of the temporary file in the file explorer.
    session_mocker.patch(
        "depythel_clt.main.click.launch",
        return_value=None,
    )

    with runner.isolated_filesystem(temp_dir=tmp_path) as directory:
        result = runner.invoke(
            depythel, ["visualise", f"{directory}/tree.html", "{'a': 'b'}"]
        )
        assert result.exit_code == 0
        assert os.path.exists(f"{directory}/tree.html")


class TestTopologicalSort:
    def test_standard(self) -> None:
        """Standard topological sorting."""
        runner = CliRunner()
        result = runner.invoke(depythel, ["topological", "{'a': 'b', 'b': 'c'}"])
        assert result.exit_code == 0
        assert result.output.replace("\n", "") == "cba"

    def test_cycle(self) -> None:
        """Cycle present in tree - No topological sorting possible."""
        runner = CliRunner()
        result = runner.invoke(depythel, ["topological", "{'a': 'b', 'b': 'a'}"])
        assert result.exit_code == 1


class TestCycleCheck:
    def test_no_cycle(self) -> None:
        """Tests no cycle output from depythel cycle."""
        runner = CliRunner()
        result = runner.invoke(depythel, ["cycle", "a", "{'a': 'b', 'b': 'c'}"])
        assert result.output.strip() == "False"

    def test_cycle(self) -> None:
        """Tests the output of depythel cycle when there is a cycle present."""
        runner = CliRunner()
        result = runner.invoke(depythel, ["cycle", "a", "{'a': 'b', 'b': 'a'}"])
        assert result.output.strip() == "True"


def test_generator(session_mocker: MockFixture) -> None:
    # Had issues with "doesn't support retrieving deps from online" from another mock
    session_mocker.stopall()
    # On the first call, the deps for gping is returned (i.e. rust)
    # on the second call, the deps for rust are returned
    session_mocker.patch(
        "depythel.repository.homebrew.online",
        side_effect=(
            {"rust": "build_dependencies"},
            {"libssh2": "dependencies", "openssl@1.1": "dependencies"},
        ),
    )
    runner = CliRunner()
    result = runner.invoke(depythel, ["generate", "gping", "homebrew", "2"])
    assert result.exit_code == 0
    # Remove all newlines and spaces via split and join
    # Based on https://www.adamsmith.haus/python/answers/how-to-remove-spaces,-tabs,-and-newlines-in-a-string-in-python
    assert (
        "".join(result.output.split())
        == '{"gping":{"rust":"build_dependencies"},"rust":{"libssh2":"dependencies","openssl@1.1":"dependencies"}}'
    )
