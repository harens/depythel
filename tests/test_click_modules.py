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

import pytest
from click import Argument, Command, Context, exceptions

from depythel_clt._click_modules import TREE_TYPE, repository_complete


# N.B. The results of these tests could change if more modules are added.
# Add tests where it is obvious what the result will be
class TestRepositoryComplete:
    def test_homebrew(self) -> None:
        """Provide autocomplete suggestions for homebrew."""
        assert repository_complete(
            Context(Command("something")), Argument(["something"]), "brew"
        ) == ["homebrew"]
        assert repository_complete(
            Context(Command("something")), Argument(["something"]), "home"
        ) == ["homebrew"]

    def test_aur(self) -> None:
        """Provide autocomplete suggestions for the AUR."""
        assert repository_complete(
            Context(Command("something")), Argument(["something"]), "au"
        ) == ["aur"]


def test_tree_conversion() -> None:
    """Test converting the terminal input of a tree in a string into a tree."""
    # Notice the apostrophes of the tree.
    assert TREE_TYPE.convert('{"a": "b", "b": "a"}', None, None) == {"a": "b", "b": "a"}
    assert TREE_TYPE.convert("{'a': 'b', 'b': 'a'}", None, None) == {"a": "b", "b": "a"}
    with pytest.raises(exceptions.BadParameter):
        TREE_TYPE.convert("not a valid tree", None, None)
