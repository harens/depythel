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

"""Stub file for networkx.classes.digraph integration with mypy.

This isn't perfect, and is created with depythel usage in mind.
"""

from typing import Any, Union

from networkx.classes.graph import Graph

# From typing imports
# Maybe find a way to import from the file?
StandardTree = dict[str, str]
DescriptiveTree = dict[str, dict[str, str]]
GraphType = Union[StandardTree, DescriptiveTree]

class DiGraph(Graph):
    graph_attr_dict_factory: Any
    node_dict_factory: Any
    node_attr_dict_factory: Any
    adjlist_outer_dict_factory: Any
    adjlist_inner_dict_factory: Any
    edge_attr_dict_factory: Any
    graph: Any
    def __init__(self, incoming_graph_data: None | GraphType = ..., **attr) -> None: ...
    @property
    def adj(self): ...
    @property
    def succ(self): ...
    @property
    def pred(self): ...
    def add_node(self, node_for_adding, **attr) -> None: ...
    def add_nodes_from(self, nodes_for_adding, **attr) -> None: ...
    def remove_node(self, n) -> None: ...
    def remove_nodes_from(self, nodes) -> None: ...
    def add_edge(self, u_of_edge, v_of_edge, **attr) -> None: ...
    def add_edges_from(self, ebunch_to_add, **attr) -> None: ...
    def remove_edge(self, u, v) -> None: ...
    def remove_edges_from(self, ebunch) -> None: ...
    def has_successor(self, u, v): ...
    def has_predecessor(self, u, v): ...
    def successors(self, n): ...
    neighbors: Any
    def predecessors(self, n): ...
    @property
    def edges(self): ...
    out_edges: Any
    @property
    def in_edges(self): ...
    @property
    def degree(self): ...
    @property
    def in_degree(self): ...
    @property
    def out_degree(self): ...
    def clear(self) -> None: ...
    def clear_edges(self) -> None: ...
    def is_multigraph(self): ...
    def is_directed(self): ...
    def to_undirected(self, reciprocal: bool = ..., as_view: bool = ...): ...
    def reverse(self, copy: bool = ...): ...
