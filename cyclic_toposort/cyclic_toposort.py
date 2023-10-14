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

    # TODO: Determine the minimal groupings graph topology for each set of cyclic edges and return the one with the
    #  least amount of groupings

    """
    # If graph has cyclic edges and is not acyclic to begin with
    if cyclic_edges[0]:
        min_groupings_graph_topology = None
        min_groupings_graph_topology_len = sys.maxsize
        # Determine the set of cyclic edges that leads to a topological sorting with the least amount of topological
        # groupings
        for cyclic_edges_set in cyclic_edges:
            reduced_edges = edges - cyclic_edges_set
            graph_topology = acyclic_toposort(reduced_edges)
            if len(graph_topology) < min_groupings_graph_topology_len:
                min_groupings_graph_topology = (graph_topology, cyclic_edges_set)
                min_groupings_graph_topology_len = len(graph_topology)
    else:
        # Determine the minimal groupings graph topology by acyclic sorting the original graph
        min_groupings_graph_topology = (acyclic_toposort(edges), set())

    return min_groupings_graph_topology
    """


def _cyclic_toposort_recursive(node_ins, node_outs) -> [{(int, int)}]:
    """Recursive part of the cyclic toposort algorithm, taking a graph as input that is represented through all its
    nodes and its according inputs and outputs.

    Returns all minimal sets of cyclic connections that would create an order for the graph.
    :param node_ins: dict (keys: int, values: {int}), specifying all nodes that have an incoming edge to the respective
        node
    :param node_outs: dict (keys: int, values: {int}), specifying all nodes that have an outgoing edge to the respective
        node
    :return: All minimal sets of cyclic edges (2-tuples) that would make the grpah acyclic and therefore sortable.
    """
    cyclic_edges = [set()]

    while True:
        #### FORWARD SORTING ###########################################################################################
        # Determine nodes with no incoming edges in current state of sorting which therefore can be placed and removed
        # from consideration
        dependencyless = set()
        for node, incomings in node_ins.items():
            if len(incomings) == 0:
                dependencyless.add(node)

        if not dependencyless:
            #### BACKWARD SORTING ######################################################################################
            while True:
                # Determine nodes with no outgoing edges in current state of sorting which therefore can be placed and
                # removed from consideration
                followerless = set()
                for node, outgoings in node_outs.items():
                    if len(outgoings) == 0:
                        followerless.add(node)

                if not followerless:
                    #### CYCLE RESOLUTION ##############################################################################
                    min_number_cyclic_edges = sys.maxsize

                    # Recreate edge list from current state of node_ins
                    edges = []
                    for node, incomings in node_ins.items():
                        for edge_start in incomings:
                            edges.append((edge_start, node))

                    # Iteratively and randomly declare more and more edges as cyclic and see how well the resulting
                    # graph (represented as reduced_node_ins and reduced_node_outs) is sortable.
                    for reduced_node_ins, reduced_node_outs, necessary_cyclic_edges in create_reduced_node_ins_outs(
                        edges,
                        node_ins,
                        node_outs,
                    ):
                        # If the necessary cyclic edges from now on are higher than the already found minimum number
                        # of cyclic edges then break
                        if len(necessary_cyclic_edges) > min_number_cyclic_edges:
                            break

                        # Recursively check for the minimum amount of cyclic edges in the resulting restgraph
                        cyclic_edges_restgraph = _cyclic_toposort_recursive(
                            reduced_node_ins,
                            reduced_node_outs,
                        )

                        # If a new minimal amount of cyclic edges has been found update the min_number_cyclic_edges
                        # variables and only save the new min cyclic edges
                        if len(necessary_cyclic_edges) + len(cyclic_edges_restgraph[0]) < min_number_cyclic_edges:
                            min_number_cyclic_edges = len(necessary_cyclic_edges) + len(cyclic_edges_restgraph[0])
                            cyclic_edges = []
                            for cyclic_edges_restgraph_set in cyclic_edges_restgraph:
                                cyclic_edges.append(cyclic_edges_restgraph_set.union(necessary_cyclic_edges))
                        # If a set of cyclic edges has been found that has the same size as the current minimum,
                        # save these cyclic edges as well
                        elif len(necessary_cyclic_edges) + len(cyclic_edges_restgraph[0]) == min_number_cyclic_edges:
                            for cyclic_edges_restgraph_set in cyclic_edges_restgraph:
                                cyclic_edges.append(cyclic_edges_restgraph_set.union(necessary_cyclic_edges))

                    break
                    ####################################################################################################

                # Remove nodes with no outgoing edges from consideration
                for node in followerless:
                    del node_outs[node]
                    del node_ins[node]

                # Remove nodes that were placed/removed from consideration of being following nodes of other nodes
                for node, outgoings in node_outs.items():
                    node_outs[node] = outgoings - followerless

            break
            ############################################################################################################

        # Remove nodes with no incoming edges from consideration
        for node in dependencyless:
            del node_ins[node]
            del node_outs[node]

        # Break if all nodes are placed
        if not node_ins:
            break

        # Remove nodes that were placed/removed from consideration of being necessary nodes of other nodes
        for node, incomings in node_ins.items():
            node_ins[node] = incomings - dependencyless
        ################################################################################################################

    return cyclic_edges
