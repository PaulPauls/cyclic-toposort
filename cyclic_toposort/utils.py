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
from copy import deepcopy


def create_reduced_node_ins_outs(edges, node_ins, node_outs) -> ({int: {int}}, {int: {int}}, {(int, int)}):
    """Iteratively and randomly select more and more edges, declare them as cyclic and return a deepcopied node_ins and
    node_outs with the cyclic edge removed.
    :param edges: Set of 2-tuples, with the 2-tuples specifying the start and end node of an edge
    :param node_ins: dict (keys: int, values: {int}), specifying all nodes that have an incoming edge to the respective
        node
    :param node_outs: dict (keys: int, values: {int}), specifying all nodes that have an outgoing edge to the respective
        node
    :return: deepcopied node_ins with the cyclic edge removed, deepcopied node_outs with the cyclic edge removed,
        cyclic edge.
    """
    for n in range(1, len(edges) + 1):
        for necessary_cyclic_edges in itertools.combinations(edges, n):
            reduced_node_ins = deepcopy(node_ins)
            reduced_node_outs = deepcopy(node_outs)
            for edge_start, edge_end in necessary_cyclic_edges:
                reduced_node_ins[edge_end] -= {edge_start}
                reduced_node_outs[edge_start] -= {edge_end}
            yield reduced_node_ins, reduced_node_outs, set(necessary_cyclic_edges)
