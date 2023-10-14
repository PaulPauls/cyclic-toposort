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
from collections.abc import Iterator
from copy import deepcopy


def generate_reduced_ins_outs(
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
