import os
import random
import time

import test_utils
from graphviz import Digraph

import cyclic_toposort


def test_create_random_graph():
    """Creating multiple graphs with random parameters and visualizing them in seperate directoy."""
    graph_viz_dir = os.path.dirname(os.path.realpath(__file__)) + "/random_test_graphs/"
    os.makedirs(graph_viz_dir, exist_ok=True)

    for i in range(100):
        num_edges = random.randint(6, 24)
        start_node = random.choice([None, random.randint(1, 5)])
        end_node = random.choice([None, random.randint(6, 10)])
        full_cyclic_graph = bool(start_node is None and end_node is None)
        cyclic_nodes = random.choice([True, False])
        nodes, edges = test_utils.create_random_graph(num_edges=num_edges,
                                                      start_node=start_node,
                                                      end_node=end_node,
                                                      full_cyclic_graph=full_cyclic_graph,
                                                      cyclic_nodes=cyclic_nodes)

        dot = Digraph(graph_attr={"rankdir": "TB"})
        for (edge_start, edge_end) in edges:
            dot.edge(str(edge_start), str(edge_end))

        dot.render(filename=f"random_test_graph_{i}", directory=graph_viz_dir, view=False, cleanup=True, format="svg")


def test_bruteforce_cyclic_graph_topologies():
    """Showcase bruteforcing of minimal topologies for random cyclic graphs."""
    num_edges = random.randint(6, 24)
    start_node = random.choice([None, random.randint(1, 5)])
    end_node = random.choice([None, random.randint(6, 10)])
    full_cyclic_graph = bool(start_node is None and end_node is None)
    cyclic_nodes = random.choice([True, False])
    nodes, edges = test_utils.create_random_graph(num_edges=num_edges,
                                                  start_node=start_node,
                                                  end_node=end_node,
                                                  full_cyclic_graph=full_cyclic_graph,
                                                  cyclic_nodes=cyclic_nodes)

    print(f"nodes: {nodes}")
    print(f"edges: {edges}")

    t_start = time.time()
    bruteforced_cyclic_graph_topologies = test_utils.bruteforce_cyclic_graph_topologies(nodes=nodes,
                                                                                        edges=edges,
                                                                                        start_node=start_node,
                                                                                        end_node=end_node)
    t_end = time.time()
    print(f"bruteforced cyclic graph topologies: {bruteforced_cyclic_graph_topologies}")
    print(f"bruteforce time: {t_end - t_start}\n")


def test_cyclic_toposort():
    """"""
    t_total_cyclic_toposort = 0
    t_total_cyclic_toposort_groupings = 0
    t_total_cyclic_toposort_bruteforce = 0
    cyclic_toposort_correct_log = True
    cyclic_toposort_groupings_correct_log = True

    for i in range(1000):
        print(f"Run {i}")

        num_edges = random.randint(8, 16)
        start_node = random.choice([None, random.randint(1, 5)])
        end_node = random.choice([None, random.randint(6, 10)])
        full_cyclic_graph = False  # Too complex given the high number of random tests
        cyclic_nodes = random.choice([True, False])
        nodes, edges = test_utils.create_random_graph(num_edges=num_edges,
                                                      start_node=start_node,
                                                      end_node=end_node,
                                                      full_cyclic_graph=full_cyclic_graph,
                                                      cyclic_nodes=cyclic_nodes)

        print(f"nodes: {nodes}")
        print(f"edges: {edges}")
        print(f"start_node: {start_node}")
        print(f"end_node: {end_node}")

        dot = Digraph(graph_attr={"rankdir": "TB"})
        for (edge_start, edge_end) in edges:
            dot.edge(str(edge_start), str(edge_end))

        dot.render(view=False, cleanup=True, format="svg")

        t_start = time.time()
        cyclic_toposort_graph_topology = cyclic_toposort.cyclic_toposort(edges=edges,
                                                                         start_node=start_node,
                                                                         end_node=end_node)
        t_end = time.time()
        print(f"cyclic toposort graph topology: {cyclic_toposort_graph_topology}")
        print(f"cyclic toposort time: {t_end - t_start}")
        t_total_cyclic_toposort += (t_end - t_start)

        t_start = time.time()
        cyclic_toposort_groupings_graph_topology = cyclic_toposort.cyclic_toposort_groupings(edges=edges,
                                                                                             start_node=start_node,
                                                                                             end_node=end_node)
        t_end = time.time()
        print(f"cyclic toposort groupings graph topology: {cyclic_toposort_groupings_graph_topology}")
        print(f"cyclic toposort groupings time: {t_end - t_start}")
        t_total_cyclic_toposort_groupings += (t_end - t_start)

        t_start = time.time()
        bruteforced_cyclic_graph_topologies = test_utils.bruteforce_cyclic_graph_topologies(nodes=nodes,
                                                                                            edges=edges,
                                                                                            start_node=start_node,
                                                                                            end_node=end_node)
        t_end = time.time()
        print(f"bruteforced cyclic graph topologies: {bruteforced_cyclic_graph_topologies}")
        print(f"bruteforce time: {t_end - t_start}")
        t_total_cyclic_toposort_bruteforce += (t_end - t_start)

        cyclic_toposort_correct_flag = True
        if len(cyclic_toposort_graph_topology[1]) != len(bruteforced_cyclic_graph_topologies[0][1]):
            cyclic_toposort_correct_flag = False

        for (edge_start, edge_end) in edges:
            if edge_start == edge_end or (edge_start, edge_end) in cyclic_toposort_graph_topology[1]:
                continue
            edge_start_index = None
            edge_end_index = None
            for index, node in enumerate(cyclic_toposort_graph_topology[0]):
                if node == edge_start:
                    edge_start_index = index
                if node == edge_end:
                    edge_end_index = index
            if edge_start_index >= edge_end_index:
                cyclic_toposort_correct_flag = False

        print(f"cyclic toposort result correct: {cyclic_toposort_correct_flag}")
        cyclic_toposort_correct_log &= cyclic_toposort_correct_flag

        print("cyclic toposort groupings result one of the bruteforced and therefore correct: {}"
              .format(cyclic_toposort_groupings_graph_topology in bruteforced_cyclic_graph_topologies))
        cyclic_toposort_groupings_correct_log &= \
            cyclic_toposort_groupings_graph_topology in bruteforced_cyclic_graph_topologies

    print(f"Total time cyclic toposort: {t_total_cyclic_toposort}")
    print(f"Total time cyclic toposort groupings: {t_total_cyclic_toposort_groupings}")
    print(f"Total time cyclic toposort bruteforce: {t_total_cyclic_toposort_bruteforce}")

    print(f"Cyclic toposort always correct: {cyclic_toposort_correct_log}")
    print(f"Cyclic toposort groupings always correct: {cyclic_toposort_groupings_correct_log}")
    assert cyclic_toposort_correct_log
    assert cyclic_toposort_groupings_correct_log


if __name__ == "__main__":
    test_create_random_graph()
    test_bruteforce_cyclic_graph_topologies()
    test_cyclic_toposort()
