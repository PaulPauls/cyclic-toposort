"""Tests for the cyclic_toposort module."""
import random

from cyclic_toposort import cyclic_toposort
from tests.test_utils import bruteforce_toposort, create_random_graph


def test_random_graphs_against_bruteforce() -> None:
    """Test cyclic_toposort with randomly generated graphs against bruteforced solutions."""
    for i in range(100):
        num_edges = random.randint(1, 12)
        cyclic_nodes = random.choice([True, False])
        edges = create_random_graph(num_edges=num_edges, cyclic_nodes=cyclic_nodes)

        print(i)

        algorithm_results = cyclic_toposort(edges=edges)
        print("+")

        bruteforce_results = bruteforce_toposort(edges=edges)
        print("-")


if __name__ == "__main__":
    test_random_graphs_against_bruteforce()
