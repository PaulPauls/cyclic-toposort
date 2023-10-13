"""
Copyright (c) 2020 Paul Pauls

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import itertools
from copy import deepcopy


def acyclic_toposort(edges) -> [{int}]:
    """
    Create topological sorting of an acyclic graph with maximized groupings of levels. Return this topological sorting
    as list of sets that represent each topological level beginning with the start (= dependencyless) nodes of the
    acyclic graph.
    :param edges: iterable of 2-tuples, specifying start and end for each edge
    :return: topological sorting of graph as list of sets that represent each topological level beginning with the start
             nodes
    """
    # Create python dict that associates each node with the set of all nodes that having an incoming edge (node_ins) to
    # that particular node. If a node has no incoming connections will the node be associated with an empty set.
    node_ins = dict()
    for (edge_start, edge_end) in edges:
        # Don't consider cyclic node edges as not relevant for topological sorting
        if edge_start == edge_end:
            continue

        if edge_start not in node_ins:
            node_ins[edge_start] = set()

        if edge_end not in node_ins:
            node_ins[edge_end] = {edge_start}
        else:
            node_ins[edge_end].add(edge_start)

    graph_topology = list()

    while True:
        # Determine all nodes having no input/dependency in the current topological level
        dependencyless = set()
        for node, incomings in node_ins.items():
            if len(incomings) == 0:
                dependencyless.add(node)

        if not dependencyless:
            if not node_ins:
                raise RuntimeError("Invalid graph detected")
            else:
                raise RuntimeError("Cyclic graph detected in acyclic_toposort function")

        # Set dependencyless nodes as the nodes of the next topological level
        graph_topology.append(dependencyless)

        # Remove dependencyless nodes from node_ins collection, as those dependencyless nodes have been placed.
        for node in dependencyless:
            del node_ins[node]

        # If all nodes are placed, exit topological sorting
        if not node_ins:
            break

        # Remove depdencyless nodes from node_ins (the set of required incoming nodes) as those dependencyless nodes
        # have been placed and their dependency to other nodes is therefore fulfilled
        for node, incomings in node_ins.items():
            node_ins[node] = incomings - dependencyless

    return graph_topology


def cyclic_toposort(edges, start_node=None, end_node=None) -> ([int], {(int, int)}):
    """
    Sorts directed cyclic graphs given the edges that define the graph and potential start_node or end_node constraints.
    The function returns a 2-tuple consisting of an ordered list of nodes as well as a set of 2-tuples being the
    necessary minmal cyclic edges.

    :param edges: Set of 2-tuples, with the 2-tuples specifying the start and end node of an edge
    :param start_node: int (optional), a node with which the sorted list of nodes should start
    :param end_node: int (optional), a node with which the sorted list of nodes should end
    :return: 2-tuple of ordered list of nodes and the minimal set of cyclic edges
    """
    # Process edges by determining the incoming and outgoing connections for each node
    node_ins = dict()
    node_outs = dict()
    cyclic_edges = set()
    for (edge_start, edge_end) in edges:
        # Don't consider cyclic node edges as not relevant for topological sorting
        if edge_start == edge_end:
            continue

        # Make sure nodes are considered in the incoming/outgoing nodes dicts even if they have no incoming/outgoing
        # edge
        if edge_start not in node_ins:
            node_ins[edge_start] = set()
        if edge_end not in node_outs:
            node_outs[edge_end] = set()

        # If start or endnodes are supplied then violating edges are automatically considered cyclic
        if start_node and edge_end == start_node:
            cyclic_edges.add((edge_start, start_node))
            continue
        if end_node and edge_start == end_node:
            cyclic_edges.add((end_node, edge_end))
            continue

        if edge_end not in node_ins:
            node_ins[edge_end] = {edge_start}
        else:
            node_ins[edge_end].add(edge_start)

        if edge_start not in node_outs:
            node_outs[edge_start] = {edge_end}
        else:
            node_outs[edge_start].add(edge_end)

    # Recursively sort the graph, finding the minimal number of cyclic edges
    cyclic_edges_restgraph = _cyclic_toposort_recursive(node_ins, node_outs)

    # Add the required edges due to optionally supplied start/end nodes to the minimal number of cyclic edges
    cyclic_edges = cyclic_edges.union(cyclic_edges_restgraph)

    # Create a set of reduced edges that would create an acyclic graph
    reduced_edges = edges - cyclic_edges

    # Process reduced edges by determining the incoming edges
    node_ins = dict()
    for (edge_start, edge_end) in reduced_edges:
        # Don't consider cyclic node edges as not relevant for topological sorting
        if edge_start == edge_end:
            continue

        # Make sure nodes are considered in the incoming nodes dict even if they have no incoming edge
        if edge_start not in node_ins:
            node_ins[edge_start] = set()

        # Disregard start/end node as they are applied later
        if start_node and edge_end == start_node:
            continue
        if end_node and edge_end == end_node:
            continue

        if edge_end not in node_ins:
            node_ins[edge_end] = {edge_start}
        else:
            node_ins[edge_end].add(edge_start)

    if start_node:
        graph_topology = [start_node]
    else:
        graph_topology = list()

    # Perform simple acyclic topological sorting of the restgraph
    while True:
        # Determine nodes with no incoming edges in current state of sorting which therefore can be placed and removed
        # from consideration
        dependencyless = set()
        for node, incomings in node_ins.items():
            if len(incomings) == 0:
                dependencyless.add(node)

        if not dependencyless:
            raise RuntimeError("Invalid graph detected")

        # Set dependencyless nodes as the nodes of the next topological level
        graph_topology += list(dependencyless)

        # Remove nodes with no incoming edges from consideration
        for node in dependencyless:
            del node_ins[node]

        # Break if all nodes are placed
        if not node_ins:
            break

        # Remove nodes that were placed/removed from consideration of being necessary nodes of other nodes
        for node, incomings in node_ins.items():
            node_ins[node] = incomings - dependencyless

    # Add optional end node if set
    if end_node:
        graph_topology += [end_node]

    return (graph_topology, cyclic_edges)


def _cyclic_toposort_recursive(node_ins, node_outs) -> {(int, int)}:
    """
    Recursive part of the cyclic toposort algorithm, taking a graph as input that is represented through all its nodes
    and its according inputs and outputs. Returns a minimal set of cyclic connections that would create an order for
    the graph.
    :param node_ins: dict (keys: int, values: {int}), specifying all nodes that have an incoming edge to the respective
        node
    :param node_outs: dict (keys: int, values: {int}), specifying all nodes that have an outgoing edge to the respective
        node
    :return: minimal set of cyclic edges (2-tuples) that would make the grpah acyclic and therefore sortable
    """
    cyclic_edges = set()

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
                    edges = list()
                    for node, incomings in node_ins.items():
                        for edge_start in incomings:
                            edges.append((edge_start, node))

                    # Iteratively and randomly declare more and more edges as cyclic and see how well the resulting
                    # graph (represented as reduced_node_ins and reduced_node_outs) is sortable.
                    for reduced_node_ins, reduced_node_outs, necessary_cyclic_edges in \
                            _create_reduced_node_ins_outs(edges, node_ins, node_outs):

                        # If the necessary cyclic edges from now on are higher than the already found minimum number
                        # of cyclic edges then break
                        if len(necessary_cyclic_edges) > min_number_cyclic_edges:
                            break

                        # Recursively check for the minimum amount of cyclic edges in the resulting restgraph
                        cyclic_edges_restgraph = _cyclic_toposort_recursive(reduced_node_ins, reduced_node_outs)

                        # If a new minimal amount of cyclic edges has been found save it
                        if len(necessary_cyclic_edges) + len(cyclic_edges_restgraph) < min_number_cyclic_edges:
                            min_number_cyclic_edges = len(necessary_cyclic_edges) + len(cyclic_edges_restgraph)
                            cyclic_edges = necessary_cyclic_edges.union(cyclic_edges_restgraph)

                            # If the restgraph is acyclic break search
                            if len(cyclic_edges_restgraph) == 0:
                                break
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


def cyclic_toposort_groupings(edges, start_node=None, end_node=None) -> ([{int}], {(int, int)}):
    """
    Sorts directed cyclic graphs given the edges that define the graph and potential start_node or end_node constraints.
    The function returns a 2-tuple consisting of an ordered list of set of nodes as well as a set of 2-tuples being the
    necessary minimal cyclic edges. Each set of nodes represents a topological level.

    :param edges: Set of 2-tuples, with the 2-tuples specifying the start and end node of an edge
    :param start_node: int (optional), a node with which the sorted list of nodes should start
    :param end_node: int (optional), a node with which the sorted list of nodes should end
    :return: 2-tuple of ordered list of set of nodes and the minimal set of cyclic edges
    """
    # Process edges by determining the incoming and outgoing connections for each node
    node_ins = dict()
    node_outs = dict()
    start_end_cyclic_edges = set()
    for (edge_start, edge_end) in edges:
        # Don't consider cyclic node edges as not relevant for topological sorting
        if edge_start == edge_end:
            continue

        # Make sure nodes are considered in the incoming/outgoing nodes dicts even if they have no incoming/outgoing
        # edge
        if edge_start not in node_ins:
            node_ins[edge_start] = set()
        if edge_end not in node_outs:
            node_outs[edge_end] = set()

        # If start or endnodes are supplied then violating edges are automatically considered cyclic
        if start_node and edge_end == start_node:
            start_end_cyclic_edges.add((edge_start, start_node))
            continue
        if end_node and edge_start == end_node:
            start_end_cyclic_edges.add((end_node, edge_end))
            continue

        if edge_end not in node_ins:
            node_ins[edge_end] = {edge_start}
        else:
            node_ins[edge_end].add(edge_start)

        if edge_start not in node_outs:
            node_outs[edge_start] = {edge_end}
        else:
            node_outs[edge_start].add(edge_end)

    # Recursively sort the graph, finding all minmal sets cyclic edges that would make the graph acyclic
    cyclic_edges_restgraph = _cyclic_toposort_groupings_recursive(node_ins, node_outs)

    # Add all necessary cyclic edges stemming from the set start/end node to the determined minimal sets of cyclic edges
    cyclic_edges = list()
    for cyclic_edges_restgraph_set in cyclic_edges_restgraph:
        cyclic_edges.append(cyclic_edges_restgraph_set.union(start_end_cyclic_edges))

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

    # If end node is specially set but it is not in the last topological level remove end node from other levels and
    # add it in the last level
    if end_node and end_node not in min_groupings_graph_topology[0][-1]:
        for grouping in min_groupings_graph_topology[0]:
            grouping -= {end_node}
        min_groupings_graph_topology[0][-1].add(end_node)

    return min_groupings_graph_topology


def _cyclic_toposort_groupings_recursive(node_ins, node_outs) -> [{(int, int)}]:
    """
    Recursive part of the cyclic toposort algorithm, taking a graph as input that is represented through all its nodes
    and its according inputs and outputs. Returns all minimal sets of cyclic connections that would create an order for
    the graph.
    :param node_ins: dict (keys: int, values: {int}), specifying all nodes that have an incoming edge to the respective
        node
    :param node_outs: dict (keys: int, values: {int}), specifying all nodes that have an outgoing edge to the respective
        node
    :return: All minimal sets of cyclic edges (2-tuples) that would make the grpah acyclic and therefore sortable
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
                    edges = list()
                    for node, incomings in node_ins.items():
                        for edge_start in incomings:
                            edges.append((edge_start, node))

                    # Iteratively and randomly declare more and more edges as cyclic and see how well the resulting
                    # graph (represented as reduced_node_ins and reduced_node_outs) is sortable.
                    for reduced_node_ins, reduced_node_outs, necessary_cyclic_edges in \
                            _create_reduced_node_ins_outs(edges, node_ins, node_outs):

                        # If the necessary cyclic edges from now on are higher than the already found minimum number
                        # of cyclic edges then break
                        if len(necessary_cyclic_edges) > min_number_cyclic_edges:
                            break

                        # Recursively check for the minimum amount of cyclic edges in the resulting restgraph
                        cyclic_edges_restgraph = _cyclic_toposort_groupings_recursive(reduced_node_ins,
                                                                                      reduced_node_outs)

                        # If a new minimal amount of cyclic edges has been found update the min_number_cyclic_edges
                        # variables and only save the new min cyclic edges
                        if len(necessary_cyclic_edges) + len(cyclic_edges_restgraph[0]) < min_number_cyclic_edges:
                            min_number_cyclic_edges = len(necessary_cyclic_edges) + len(cyclic_edges_restgraph[0])
                            cyclic_edges = list()
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


def _create_reduced_node_ins_outs(edges, node_ins, node_outs) -> ({int: {int}}, {int: {int}}, {(int, int)}):
    """
    Iteratively and randomly select more and more edges, declare them as cyclic and return a deepcopied node_ins and
    node_outs with the cyclic edge removed.
    :param edges: Set of 2-tuples, with the 2-tuples specifying the start and end node of an edge
    :param node_ins: dict (keys: int, values: {int}), specifying all nodes that have an incoming edge to the respective
        node
    :param node_outs: dict (keys: int, values: {int}), specifying all nodes that have an outgoing edge to the respective
        node
    :return: deepcopied node_ins with the cyclic edge removed, deepcopied node_outs with the cyclic edge removed,
        cyclic edge
    """
    for n in range(1, len(edges) + 1):
        for necessary_cyclic_edges in itertools.combinations(edges, n):
            reduced_node_ins = deepcopy(node_ins)
            reduced_node_outs = deepcopy(node_outs)
            for (edge_start, edge_end) in necessary_cyclic_edges:
                reduced_node_ins[edge_end] -= {edge_start}
                reduced_node_outs[edge_start] -= {edge_end}
            yield reduced_node_ins, reduced_node_outs, set(necessary_cyclic_edges)
