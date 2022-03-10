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

"""Provides general utility functions for use within different modules.

Deals with built-in library API changes between different Python versions.
The main fix is dealing with aspects of the typing module being depreciated.
"""

# Please keep types in alphabetical order. Thanks.

import sys
from typing import Union

# TODO: For some reason, it wants the type parameters with tuple
# error: Missing type parameters for generic type "tuple"

# Don't count code coverage since different python versions
# won't run different parts of code
if sys.version_info >= (3, 9):  # pragma: no cover
    from collections import deque
    from collections.abc import Generator
    from functools import cache

    CacheType = cache
    DequeType = deque
    DictType = dict
    GeneratorType = Generator
    ListType = list
    SetType = set
else:  # pragma: no cover
    from functools import lru_cache
    from typing import Deque, Dict, Generator, List, Set

    CacheType = lru_cache(maxsize=None)
    DequeType = Deque
    DictType = Dict
    GeneratorType = Generator
    ListType = List
    SetType = Set

# Standard tree e.g. {'a': 'b', 'b': 'a'}
# A descriptive tree might show dependency type e.g. runtime/build
StandardTree = DictType[str, str]  # pylint: disable=unsubscriptable-object
DescriptiveTree = DictType[
    str, DictType[str, str]
]  # pylint: disable=unsubscriptable-object
AnyTree = Union[StandardTree, DescriptiveTree]
