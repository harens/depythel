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

"""Stub file for pyvis.network integration with mypy.

This isn't perfect, and is created with depythel usage in mind.
"""

from typing import Any, Union

from networkx.classes.digraph import DiGraph

class Network:
    nodes: list[dict[str, Union[str, int]]]
    edges: Any
    height: str
    width: str
    heading: Any
    html: str
    shape: str
    font_color: bool
    directed: bool
    bgcolor: str
    use_DOT: bool
    dot_lang: str
    options: Any
    widget: bool
    node_ids: Any
    node_map: Any
    template: Any
    conf: bool
    path: Any
    def __init__(
        self,
        height: str = "500px",
        width: str = "500px",
        directed: bool = False,
        notebook: bool = False,
        bgcolor: str = "#ffffff",
        font_color: bool = False,
        layout: Any | None = None,
        heading: str = "",
    ) -> None: ...
    def add_node(self, n_id, label: Any | None, shape: str, **options) -> None: ...
    def add_nodes(self, nodes, **kwargs) -> None: ...
    def num_nodes(self): ...
    def num_edges(self): ...
    def add_edge(self, source: int, to: int, **options) -> None: ...
    def add_edges(self, edges) -> None: ...
    def get_network_data(self): ...
    def save_graph(self, name) -> None: ...
    def write_html(self, name, notebook: bool): ...
    def show(self, name: str): ...
    def prep_notebook(
        self, custom_template: bool, custom_template_path: Any | None
    ) -> None: ...
    def set_template(self, path_to_template) -> None: ...
    def from_DOT(self, dot) -> None: ...
    def get_adj_list(self): ...
    def neighbors(self, node): ...
    def from_nx(
        self,
        nx_graph: Digraph,  # N.B. digraph is a depythel specific value
        node_size_transf=...,
        edge_weight_transf=...,
        default_node_size: int = 10,
        default_edge_weight: int = 1,
    ): ...
    def get_nodes(self): ...
    def get_node(self, n_id): ...
    def get_edges(self): ...
    def barnes_hut(
        self,
        gravity: int,
        central_gravity: float,
        spring_length: int,
        spring_strength: float,
        damping: float,
        overlap: int,
    ) -> None: ...
    def repulsion(
        self,
        node_distance: int,
        central_gravity: float,
        spring_length: int,
        spring_strength: float,
        damping: float,
    ) -> None: ...
    def hrepulsion(
        self,
        node_distance: int,
        central_gravity: float,
        spring_length: int,
        spring_strength: float,
        damping: float,
    ) -> None: ...
    def force_atlas_2based(
        self,
        gravity: int,
        central_gravity: float,
        spring_length: int,
        spring_strength: float,
        damping: float,
        overlap: int,
    ) -> None: ...
    def to_json(self, max_depth: int, **args): ...
    def set_edge_smooth(self, smooth_type) -> None: ...
    def toggle_hide_edges_on_drag(self, status) -> None: ...
    def toggle_hide_nodes_on_drag(self, status) -> None: ...
    def inherit_edge_colors(self, status) -> None: ...
    def show_buttons(self, filter_: Any | None) -> None: ...
    def toggle_physics(self, status) -> None: ...
    def toggle_drag_nodes(self, status) -> None: ...
    def toggle_stabilization(self, status) -> None: ...
    def set_options(self, options) -> None: ...
