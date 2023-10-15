import timeit
import random
from tests.utils import create_random_graph
from cyclic_toposort import cyclic_toposort

ITERATIONS = 10


def benchmark_function() -> None:
    """Benchmark cyclic_toposort with randomly generated graphs."""
    num_edges = random.randint(8, 12)
    cyclic_nodes = random.random() < 0.2
    edges = create_random_graph(num_edges=num_edges, cyclic_nodes=cyclic_nodes)

    cyclic_toposort(edges=edges)


elapsed_time = timeit.timeit(benchmark_function, number=ITERATIONS)

print(f"Function executed in {elapsed_time / ITERATIONS:.8f} seconds per iteration.")
