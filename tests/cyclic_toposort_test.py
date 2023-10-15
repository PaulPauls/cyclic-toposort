"""Tests for the cyclic_toposort module."""
import random
from pathlib import Path

import yaml
from graphviz import Digraph

from cyclic_toposort.cyclic_toposort import cyclic_toposort
from tests.test_utils import bruteforce_toposort, create_random_graph

TEST_GRAPHS_DIR = "./test_graphs/"
TEST_RESULTS_YAML = "./test_results.yaml"
CYCLIC_NODES_PROBABILITY = 0.2
START_NODE_PROBABILITY = 0.2


def test_random_graphs_against_bruteforce() -> None:
    """Test cyclic_toposort with randomly generated graphs against bruteforced solutions."""
    test_graphs_dir = Path(TEST_GRAPHS_DIR)
    test_graphs_dir.resolve()
    test_graphs_dir.mkdir(exist_ok=True)

    test_results_yaml = Path(TEST_RESULTS_YAML)
    test_results_yaml.resolve()

    test_results: dict[str, dict] = {}  # type: ignore[type-arg]
    for i in range(100):
        test_name = f"test_graph_{i}"

        num_edges = random.randint(8, 16)
        cyclic_nodes = random.random() < CYCLIC_NODES_PROBABILITY
        edges = create_random_graph(num_edges=num_edges, cyclic_nodes=cyclic_nodes)
        start_node = None
        if random.random() < START_NODE_PROBABILITY:
            start_node = random.choice(list(edges))[0]

        graph = Digraph(graph_attr={"rankdir": "TB"})
        for edge_start, edge_end in edges:
            graph.edge(str(edge_start), str(edge_end))
        graph.render(filename=test_name, directory=test_graphs_dir, view=False, cleanup=True, format="svg")

        algorithm_results = cyclic_toposort(edges=edges)
        bruteforce_results = bruteforce_toposort(edges=edges)
        assert algorithm_results in bruteforce_results

        test_results[test_name] = {
            "edges": edges,
            "start_node": start_node,
            "algorithm_results": algorithm_results,
            "bruteforce_results": bruteforce_results,
        }

    with test_results_yaml.open("w") as test_results_yaml_file:
        yaml.dump(test_results, test_results_yaml_file)


if __name__ == "__main__":
    test_random_graphs_against_bruteforce()
