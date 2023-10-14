"""Module providing functions for sorting directed cyclic graphs with minimal cyclic edges into topological groups."""

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

import sys

from cyclic_toposort.acyclic_toposort import acyclic_toposort
from cyclic_toposort.utils import generate_reduced_ins_outs


def cyclic_toposort(
    edges: set[tuple[int, int]],
    start_node: int | None = None,
) -> tuple[list[set[int]], set[tuple[int, int]]]:
    """"""
    node_ins: dict[int, set[int]] = {}
    node_outs: dict[int, set[int]] = {}
    cyclic_edges_forced: set[tuple[int, int]] = set()

    for edge_start, edge_end in edges:
        # Don't consider cyclic node edges as not relevant for topological sorting
        if edge_start == edge_end:
            continue

        # Ensure the nodes exist in the dictionaries
        node_ins.setdefault(edge_start, set())
        node_outs.setdefault(edge_end, set())

        # If start_node is supplied then violating edges are considered as forced cyclic edges
        if start_node and start_node == edge_end:
            cyclic_edges_forced.add((edge_start, edge_end))
            continue

        # Store the edge_start and edge_end in the node_ins and node_outs dictionaries
        node_ins.setdefault(edge_end, set()).add(edge_start)
        node_outs.setdefault(edge_start, set()).add(edge_end)

    # Recursively sort the (possibly cyclic) graph represented by the just determined node inputs and outputs, which
    # take the potential start_node constraint in consideration.
    cyclic_edges = _cyclic_toposort_recursive(
        node_ins=node_ins,
        node_outs=node_outs,
    )

    # If there are forced cyclic_edges due to a start_node constraint add them to the computed cyclic_edges
    if cyclic_edges_forced:
        for cyclic_edges_set in cyclic_edges:
            cyclic_edges_set.update(cyclic_edges_forced)

    # If graph has cyclic edges and is not acyclic to begin with
    if cyclic_edges[0]:
        min_graph_topology = None
        min_graph_topology_len = sys.maxsize
        # Among the list of sets of minimal cyclic_edges determine the set of cyclic edges that also leads to a
        # topological sorting with the least amount of topological groupings
        for cyclic_edges_set in cyclic_edges:
            reduced_edges = edges - cyclic_edges_set
            graph_topology = acyclic_toposort(reduced_edges)
            if len(graph_topology) < min_graph_topology_len:
                min_graph_topology = (graph_topology, cyclic_edges_set)
                min_graph_topology_len = len(graph_topology)
    else:
        # As the graph is acyclic return a simple acylic topological sorting with an empty set of cyclic edges
        min_graph_topology = (acyclic_toposort(edges), set())

    return min_graph_topology


def _cyclic_toposort_recursive(
    node_ins: dict[int, set[int]],
    node_outs: dict[int, set[int]],
) -> list[set[tuple[int, int]]]:
    """"""
    cyclic_edges: list[set[tuple[int, int]]] = [set()]

    while True:
        #### FORWARD SORTING ###########################################################################################
        # Determine nodes with no incoming edges in current state of sorting which therefore can be placed and removed
        # from consideration
        dependencyless = {node for node, incomings in node_ins.items() if not incomings}

        if not dependencyless:
            #### BACKWARD SORTING ######################################################################################
            while True:
                # Determine nodes with no outgoing edges in current state of sorting which therefore can be placed and
                # removed from consideration
                followerless = {node for node, outgoings in node_outs.items() if not outgoings}

                if not followerless:
                    #### CYCLE RESOLUTION ##############################################################################
                    min_number_cyclic_edges = sys.maxsize

                    # Recreate edge list from current state of node_ins
                    edges = {
                        (edge_start, edge_end) for edge_end, incomings in node_ins.items() for edge_start in incomings
                    }

                    # Iteratively and randomly declare more and more edges as cyclic and see how well the resulting
                    # graph (represented as reduced_node_ins and reduced_node_outs) is sortable.
                    for reduced_node_ins, reduced_node_outs, forced_cyclic_edges in generate_reduced_ins_outs(
                        edges=edges,
                        node_ins=node_ins,
                        node_outs=node_outs,
                    ):
                        # Break if the necessary cyclic edges are higher than the already found minimum number of
                        # cyclic edges
                        if len(forced_cyclic_edges) > min_number_cyclic_edges:
                            break

                        # Recursively check for the minimum amount of cyclic edges in the resulting restgraph
                        reduced_cyclic_edges = _cyclic_toposort_recursive(
                            node_ins=reduced_node_ins,
                            node_outs=reduced_node_outs,
                        )

                        # If a new minimal amount of cyclic edges has been found update the min_number_cyclic_edges
                        # variables and only save the new min cyclic edges
                        total_cyclic_edges = len(forced_cyclic_edges) + len(reduced_cyclic_edges[0])
                        if total_cyclic_edges < min_number_cyclic_edges:
                            min_number_cyclic_edges = total_cyclic_edges
                            cyclic_edges = [
                                reduced_cyclic_edges_set.union(forced_cyclic_edges)
                                for reduced_cyclic_edges_set in reduced_cyclic_edges
                            ]
                        # If a set of cyclic edges has been found that has the same size as the current minimum,
                        # save these cyclic edges as well
                        elif total_cyclic_edges == min_number_cyclic_edges:
                            for reduced_cyclic_edges_set in reduced_cyclic_edges:
                                cyclic_edges.append(reduced_cyclic_edges_set.union(forced_cyclic_edges))

                    return cyclic_edges
                    ####################################################################################################

                # Remove nodes with no outgoing edges from consideration
                for node in followerless:
                    del node_ins[node]
                    del node_outs[node]

                # Remove nodes that were placed/removed from consideration of being following nodes of other nodes
                node_outs = {node: outgoings - followerless for node, outgoings in node_outs.items()}
            ############################################################################################################

        # Remove nodes with no incoming edges from consideration
        for node in dependencyless:
            del node_ins[node]
            del node_outs[node]

        # Break if all nodes are placed
        if not node_ins:
            break

        # Remove nodes that were placed/removed from consideration of being necessary nodes of other nodes
        node_ins = {node: incomings - dependencyless for node, incomings in node_ins.items()}
        ################################################################################################################

    return cyclic_edges
