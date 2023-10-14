"""Module providing utility functions for the cyclic_toposort package."""

# Copyright (c) 2020 Paul Pauls.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import itertools
from collections.abc import Iterable, Iterator
from copy import deepcopy


def generate_modified_ins_outs(
    edges: set[tuple[int, int]],
    node_ins: dict[int, set[int]],
    node_outs: dict[int, set[int]],
) -> Iterator[tuple[dict[int, set[int]], dict[int, set[int]], set[tuple[int, int]]]]:
    """Randomly select subsets of edges, treat them as cyclic, and yield modified node_ins and node_outs with those
    cyclic edges removed.

    :param edges: Set of edges, each represented as a (start_node, end_node) tuple.
    :param node_ins: Dictionary mapping nodes to sets of nodes from which they receive edges.
    :param node_outs: Dictionary mapping nodes to sets of nodes to which they send edges.
    :yield: Iterator for a 3-tuple consisting of
        - Modified node_ins with cyclic edges removed.
        - Modified node_outs with cyclic edges removed.
        - Set of edges treated as cyclic.
    """
    # Iterate over subsets of edges of increasing sizes
    for n in range(1, len(edges) + 1):
        for cyclic_edges in itertools.combinations(edges, n):
            modified_ins = deepcopy(node_ins)
            modified_outs = deepcopy(node_outs)

            # Remove cyclic edges from modified ins and outs
            for edge_start, edge_end in cyclic_edges:
                modified_ins[edge_end].discard(edge_start)
                modified_outs[edge_start].discard(edge_end)

            yield modified_ins, modified_outs, set(cyclic_edges)


def create_node_ins_outs(
    edges: Iterable[tuple[int, int]],
    start_node: int | None = None,
) -> tuple[dict[int, set[int]], dict[int, set[int]], set[tuple[int, int]]]:
    """Given the edges of a directed graph, compute the incoming and outgoing connections for each node and identify
    cyclic edges stemming from an optional start_node constraint.

    :param edges: Iterable of 2-tuples, with the 2-tuples specifying the start and end node of an edge.
    :param start_node: Optionally specified node with which the sorted list of nodes should start.
    :return: 3-tuple of
        - Dictionary mapping nodes to a set of nodes from which there's an incoming edge.
        - Dictionary mapping nodes to a set of nodes to which there's an outgoing edge.
        - Set of cyclic edges.
    """
    node_ins: dict[int, set[int]] = {}
    node_outs: dict[int, set[int]] = {}
    cyclic_edges: set[tuple[int, int]] = set()

    for edge_start, edge_end in edges:
        # Don't consider cyclic node edges as not relevant for topological sorting
        if edge_start == edge_end:
            continue

        # Ensure the nodes exist in the dictionaries
        node_ins.setdefault(edge_start, set())
        node_outs.setdefault(edge_end, set())

        # If start_node is supplied then violating edges are automatically considered cyclic
        if start_node and start_node == edge_end:
            cyclic_edges.add((edge_start, edge_end))
            continue

        # Store the edge_start and edge_end in the node_ins and node_outs dictionaries
        node_ins.setdefault(edge_end, set()).add(edge_start)
        node_outs.setdefault(edge_start, set()).add(edge_end)

    return node_ins, node_outs, cyclic_edges
