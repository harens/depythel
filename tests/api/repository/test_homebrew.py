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

"""Tests retrieving dependencies from the Homebrew repository"""

from pytest_mock import MockFixture

from depythel.api.repository.homebrew import online


def test_standard_response(session_mocker: MockFixture) -> None:
    """Standard Expected 200 response."""

    session_mocker.patch("depythel.api.repository.homebrew.urlopen")
    session_mocker.patch(
        "depythel.api.repository.homebrew.json.load",
        return_value={
            "name": "gping",
            "full_name": "gping",
            "tap": "homebrew/core",
            "oldname": None,
            "aliases": [],
            "versioned_formulae": [],
            "desc": "Ping, but with a graph",
            "license": "MIT",
            "homepage": "https://github.com/orf/gping",
            "versions": {"stable": "1.2.7", "head": "HEAD", "bottle": True},
            "urls": {
                "stable": {
                    "url": "https://github.com/orf/gping/archive/gping-v1.2.7.tar.gz",
                    "tag": None,
                    "revision": None,
                }
            },
            "revision": 0,
            "version_scheme": 0,
            "bottle": {
                "stable": {
                    "rebuild": 0,
                    "root_url": "https://ghcr.io/v2/homebrew/core",
                    "files": {
                        "arm64_monterey": {
                            "cellar": ":any_skip_relocation",
                            "url": "https://ghcr.io/v2/homebrew/core/gping/blobs/sha256:6d765ccf11cdceca6b3b1bf406cd835f3d2dff403943fbdd7710f72a1bc0945c",
                            "sha256": "6d765ccf11cdceca6b3b1bf406cd835f3d2dff403943fbdd7710f72a1bc0945c",
                        },
                        "arm64_big_sur": {
                            "cellar": ":any_skip_relocation",
                            "url": "https://ghcr.io/v2/homebrew/core/gping/blobs/sha256:1e017d379dd6aec6187488dfb82e371ab23d1dbfc8a9ed2f10dd4fe45def08db",
                            "sha256": "1e017d379dd6aec6187488dfb82e371ab23d1dbfc8a9ed2f10dd4fe45def08db",
                        },
                        "monterey": {
                            "cellar": ":any_skip_relocation",
                            "url": "https://ghcr.io/v2/homebrew/core/gping/blobs/sha256:234d9cc183fa6f405384e4b37019a7165d6f4120b74843d77da6f6a95ad58779",
                            "sha256": "234d9cc183fa6f405384e4b37019a7165d6f4120b74843d77da6f6a95ad58779",
                        },
                        "big_sur": {
                            "cellar": ":any_skip_relocation",
                            "url": "https://ghcr.io/v2/homebrew/core/gping/blobs/sha256:fb4bae7c54fd41aa3f321a805727ad1c40440bde88fb69f348901d7ae076ac28",
                            "sha256": "fb4bae7c54fd41aa3f321a805727ad1c40440bde88fb69f348901d7ae076ac28",
                        },
                        "catalina": {
                            "cellar": ":any_skip_relocation",
                            "url": "https://ghcr.io/v2/homebrew/core/gping/blobs/sha256:f480fd25f60b819c6e00883a01eb5970d4276c6c1445774554d2a74071e566c1",
                            "sha256": "f480fd25f60b819c6e00883a01eb5970d4276c6c1445774554d2a74071e566c1",
                        },
                    },
                }
            },
            "keg_only": False,
            "keg_only_reason": None,
            "bottle_disabled": False,
            "options": [],
            "build_dependencies": ["rust"],
            "dependencies": [],
            "recommended_dependencies": [],
            "optional_dependencies": [],
            "uses_from_macos": [],
            "requirements": [],
            "conflicts_with": [],
            "caveats": None,
            "installed": [],
            "linked_keg": None,
            "pinned": False,
            "outdated": False,
            "deprecated": False,
            "deprecation_date": None,
            "deprecation_reason": None,
            "disabled": False,
            "disable_date": None,
            "disable_reason": None,
            "analytics": {
                "install": {
                    "30d": {"gping": 1285, "gping --HEAD": 3},
                    "90d": {"gping": 2492, "gping --HEAD": 3},
                    "365d": {"gping": 8907, "gping --HEAD": 3},
                },
                "install_on_request": {
                    "30d": {"gping": 1282, "gping --HEAD": 3},
                    "90d": {"gping": 2492, "gping --HEAD": 3},
                    "365d": {"gping": 8897, "gping --HEAD": 3},
                },
                "build_error": {"30d": {"gping": 0}},
            },
            "analytics-linux": {
                "install": {
                    "30d": {"gping": 11},
                    "90d": {"gping": 34},
                    "365d": {"gping": 254},
                },
                "install_on_request": {
                    "30d": {"gping": 12},
                    "90d": {"gping": 34},
                    "365d": {"gping": 253},
                },
                "build_error": {"30d": {"gping": 0}},
            },
            "generated_date": "2022-01-25",
        },
    )
    assert online("gping") == {"rust": "build_dependencies"}
