"""Module for utility functions used in tests."""
import itertools
import random
import sys
from collections.abc import Iterator


def create_random_graph(
    num_edges: int,
    cyclic_nodes: bool = False,
) -> set[tuple[int, int]]:
    """Generate a random graph with the given number of edges.

    :param num_edges: The desired number of edges in the graph. Minimum of 1.
    :param cyclic_nodes: If True, allows edges to loop back to their starting node; if False, edges are strictly between
        distinct nodes.
    :return: A set of edges represented as tuples where each tuple contains two integers corresponding to node IDs.
    """
    nodes = [1, 2]
    edges = {(1, 2)}

    while len(edges) < num_edges:
        possible_new_node = max(nodes) + 1
        possible_nodes = [*nodes, possible_new_node]
        if cyclic_nodes:
            edge_start = random.choice(possible_nodes)
            edge_end = random.choice(nodes) if edge_start == possible_new_node else random.choice(possible_nodes)
        else:
            edge_start, edge_end = random.sample(possible_nodes, k=2)

        new_edge = (edge_start, edge_end)
        if new_edge not in edges:
            edges.add(new_edge)

            if possible_new_node in new_edge:
                nodes.append(possible_new_node)

    return edges


def bruteforce_cyclic_toposort(
    edges: set[tuple[int, int]],
    start_node: int | None = None,
) -> list[tuple[list[set[int]], set[tuple[int, int]]]]:
    """Determine all possible graph topologies for a given set of edges that yield a minimal number of necessary cyclic
    edges and a minimal number of necessary topological groupings.

    :param edges: A set of tuples where each tuple represents a directed edge (start_node, end_node) in the graph.
    :param start_node: An optional node. If provided, any edge leading into this node will be considered as a forced
        cyclic edge.
    :return: A list of tuples consisting of
        - A graph topology with the minimum number of topological groupings.
        - A minimal set of edges that are necessary to be considered cyclic in order to make the graph acyclic.
    """
    minimal_graph_topologies = []
    minimal_graph_topology_groupings = sys.maxsize
    minimal_cyclic_edges = sys.maxsize
    previously_checked_graph_topologies = []

    # Remove single node cyclic edges
    edges = {(edge_start, edge_end) for (edge_start, edge_end) in edges if edge_start != edge_end}
    nodes = {node for edge in edges for node in edge}

    if start_node:
        nodes.remove(start_node)

    for node_ordering in itertools.permutations(nodes):
        if start_node:
            node_ordering = (start_node, *node_ordering)  # noqa: PLW2901

        for graph_topology in create_groupings(node_ordering):
            if graph_topology in previously_checked_graph_topologies:
                continue

            previously_checked_graph_topologies.append(graph_topology)
            cyclic_edges = set()
            for edge_start, edge_end in edges:
                edge_start_index = None
                edge_end_index = None

                # Determine the level of each node in the graph topology
                for level_index in range(len(graph_topology)):
                    if edge_start in graph_topology[level_index]:
                        edge_start_index = level_index

                    if edge_end in graph_topology[level_index]:
                        edge_end_index = level_index

                    if edge_start_index is not None and edge_end_index is not None:
                        break

                # Determine if the edge is cyclic in the current graph topology
                if edge_start_index >= edge_end_index:  # type: ignore[operator]
                    cyclic_edges.add((edge_start, edge_end))

                if len(cyclic_edges) > minimal_cyclic_edges:
                    break

            if len(cyclic_edges) < minimal_cyclic_edges:
                minimal_graph_topologies = [(graph_topology, cyclic_edges)]
                minimal_graph_topology_groupings = len(graph_topology)
                minimal_cyclic_edges = len(cyclic_edges)
            elif len(cyclic_edges) == minimal_cyclic_edges:
                if len(graph_topology) < minimal_graph_topology_groupings:
                    minimal_graph_topologies = [(graph_topology, cyclic_edges)]
                    minimal_graph_topology_groupings = len(graph_topology)
                elif len(graph_topology) == minimal_graph_topology_groupings:
                    minimal_graph_topologies.append((graph_topology, cyclic_edges))

    return minimal_graph_topologies


def create_groupings(inputs: list[int] | tuple[int, ...]) -> Iterator[list[set[int]]]:
    """Generate all possible groupings of an iterable.

    :param inputs: Iterable (e.g., list) of elements
    :return: generator yielding lists of sets of grouped nodes
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
