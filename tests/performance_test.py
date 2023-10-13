import itertools
import random
import sys


def create_random_graph(
    num_edges,
    start_node=None,
    end_node=None,
    full_cyclic_graph=False,
    cyclic_nodes=False,
) -> (list, {(int, int)}):
    """Create a random graph (nodes and edges) with the specified amount of edges. The random graph can optionally have
    an explicitely set start_node or end_node, which has no incoming (or respectively outgoing) edges. If the graph is
    set to be fully cyclic then there exist no single node without at least 1 incoming and outgoing connection
    :param num_edges: int, number of edges in created random graph
    :param start_node: int (optional), node id of a start node that has no incoming connections
    :param end_node: int (optional), node id of an end node that has no outgoing connections
    :param full_cyclic_graph: bool (optional), if set then all nodes in the created graph have at least 1 incoming and
                                               1 outgoing connection
    :param cyclic_nodes: bool (optional), if set then an edge can have the same start and end node
    :return: list of node ids, set of all edges as tuples.
    """
    # No full cyclic graph can be created if start or end node is supplied
    assert (full_cyclic_graph is True and start_node is None and end_node is None) or full_cyclic_graph is False

    nodes = []
    edges = set()

    first_node = 1 if start_node is None else start_node
    second_node = 2 if end_node is None else end_node

    nodes.append(first_node)
    nodes.append(second_node)
    edges.add((first_node, second_node))
    if full_cyclic_graph:
        edges.add((second_node, first_node))

    while len(edges) < num_edges:
        possible_new_node = max(nodes) + 1
        possible_nodes = [*nodes, possible_new_node]
        if cyclic_nodes:
            edge_start = random.choice(possible_nodes)
            edge_end = random.choice(nodes) if edge_start == possible_new_node else random.choice(possible_nodes)
        else:
            edge_start, edge_end = random.sample(possible_nodes, k=2)

        # Skip connection creation if the edge would create an incoming connection for the start node or an outgoing
        # connection for the end node if either is supplied
        if (start_node and edge_end == start_node) or (end_node and edge_start == end_node):
            continue

        if (edge_start, edge_end) not in edges:
            edges.add((edge_start, edge_end))

            if full_cyclic_graph and edge_start == possible_new_node:
                full_cyclic_edge_start = random.choice(nodes)
                edges.add((full_cyclic_edge_start, edge_start))

            if full_cyclic_graph and edge_end == possible_new_node:
                full_cyclic_edge_end = random.choice(nodes)
                edges.add((edge_end, full_cyclic_edge_end))

            if edge_start == possible_new_node or edge_end == possible_new_node:
                nodes.append(possible_new_node)

    return nodes, edges


def create_groupings(inputs):
    """Create all possible groupings of an iterable as generator.
    :param inputs: iterable
    :return: generator of all possible groupings.
    """
    for n in range(1, len(inputs) + 1):
        for split_indices in itertools.combinations(range(1, len(inputs)), n - 1):
            grouping = []
            prev_split_index = None
            for split_index in itertools.chain(split_indices, [None]):
                group = set(inputs[prev_split_index:split_index])
                grouping.append(group)
                prev_split_index = split_index
            yield grouping


def bruteforce_cyclic_graph_topologies(nodes, edges, start_node=None, end_node=None) -> [([{int}], {(int, int)})]:
    """Bruteforce all graph topologies with a minimal amount of cyclic edges and a minimal amount of seperate topology
    groupings by creating all possible permutations of node orderings and groupings and saving only those with minimal
    size. The bruteforcing can be accelerated if a desired start and/or end node for the minimal topologies is supplied.
    Edges that start and end in the same node are not considered cyclic. Return all minimal graph topologies with their
    amount of cyclic edges.
    :param nodes: list of all nodes
    :param edges: iterable of 2-tuples of the start node and end node of each edge
    :param start_node: int (optional), node id of a start node that should be in first grouping of graph topology
    :param end_node: int (optional), node id of an end node that should be in last grouping of graph topology
    :return: minimal cyclic and minimal grouped graph topologies and their corresponding cyclic edges.
    """
    assert start_node is None or start_node in nodes
    assert end_node is None or end_node in nodes

    minimal_cyclic_graph_topologies = []
    minimal_graph_topology_groupings = sys.maxsize
    minimal_number_cyclic_edges = sys.maxsize
    previously_checked_graph_topologies = []

    # Remove single node cyclic edges and copy nodes in case it has been passed as reference
    edges = [(edge_start, edge_end) for (edge_start, edge_end) in edges if edge_start != edge_end]
    nodes_copy = nodes.copy()

    # Remove and later insert fixed start and end node in order to always ensure that start node is in first grouping
    # and end node is in last grouping if they are supplied.
    if start_node:
        nodes_copy.remove(start_node)
    if end_node:
        nodes_copy.remove(end_node)

    r_nodes_iter = itertools.permutations(nodes_copy)

    for ordering in r_nodes_iter:
        if start_node:
            ordering = (start_node, *ordering)
        if end_node:
            ordering = (*ordering, end_node)

        for graph_topology in create_groupings(ordering):
            # If the current graph topology has been checked before in another premutation, skip check
            if graph_topology in previously_checked_graph_topologies:
                continue
            else:
                previously_checked_graph_topologies.append(graph_topology)

            cyclic_edges = set()
            for edge_start, edge_end in edges:
                edge_start_index = None
                edge_end_index = None

                for level_index in range(len(graph_topology)):
                    if edge_start in graph_topology[level_index]:
                        edge_start_index = level_index

                    if edge_end in graph_topology[level_index]:
                        edge_end_index = level_index

                    if edge_start_index is not None and edge_end_index is not None:
                        break

                if edge_start_index >= edge_end_index:
                    cyclic_edges.add((edge_start, edge_end))

                if len(cyclic_edges) > minimal_number_cyclic_edges:
                    break

            if len(cyclic_edges) < minimal_number_cyclic_edges:
                minimal_cyclic_graph_topologies = [(graph_topology, cyclic_edges)]
                minimal_graph_topology_groupings = len(graph_topology)
                minimal_number_cyclic_edges = len(cyclic_edges)
            elif len(cyclic_edges) == minimal_number_cyclic_edges:
                if len(graph_topology) < minimal_graph_topology_groupings:
                    minimal_cyclic_graph_topologies = [(graph_topology, cyclic_edges)]
                    minimal_graph_topology_groupings = len(graph_topology)
                elif len(graph_topology) == minimal_graph_topology_groupings:
                    minimal_cyclic_graph_topologies.append((graph_topology, cyclic_edges))

    return minimal_cyclic_graph_topologies
