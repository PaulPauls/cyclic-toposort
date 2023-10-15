"""Module for utility functions used in tests."""

import random


def create_random_graph(
    num_edges: int,
    cyclic_nodes: bool = False,
) -> set[tuple[int, int]]:
    """Generate a random graph with the given number of edges.

    :param num_edges: The desired number of edges in the graph.
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
