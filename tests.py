import sys
import time
import random
import tempfile
import itertools
from graphviz import Digraph
from cyclic_toposort import cyclic_toposort

########################################################################################################################
'''
random_nodes = [0, 1]
random_conns = {(0, 1)}
while len(random_conns) < 20:

    conn_start, conn_end = random.sample(random_nodes, k=2)
    if conn_start == 1 or conn_end == 0:
        continue

    if (conn_start, conn_end) not in random_conns:
        random_conns.add((conn_start, conn_end))
    else:
        new_node = max(random_nodes) + 1
        random_nodes.append(new_node)

        random_conns.add((conn_start, new_node))
        random_conns.add((new_node, conn_end))

# random_nodes = [0, 1, 2, 3, 4, 5, 6, 7, 8]
# random_conns = {(7, 3), (2, 1), (2, 5), (0, 3), (5, 8), (3, 6), (3, 4), (4, 1), (2, 3), (0, 5), (5, 3), (0, 1),
#                 (2, 7), (8, 3), (6, 1), (3, 1), (5, 7), (0, 6), (5, 2), (0, 2)}

print(f"random_nodes: {random_nodes}")
print(f"random_conns: {random_conns}")

node_dependencies = dict()
for conn in random_conns:
    if conn[1] in node_dependencies:
        node_dependencies[conn[1]].add(conn[0])
    else:
        node_dependencies[conn[1]] = {conn[0]}

print(f"node_dependencies: {node_dependencies}")


########################################################################################################################

def create_groupings(inputs):
    list_len = len(inputs)
    for n in range(1, list_len + 1):
        for split_indices in itertools.combinations(range(1, list_len), n - 1):
            grouping = []
            grouping_tuple = []
            prev_split_index = None
            for split_index in itertools.chain(split_indices, [None]):
                group = set(inputs[prev_split_index:split_index])
                grouping.append(group)
                grouping_tuple.append(tuple(group))
                prev_split_index = split_index
            yield grouping, tuple(grouping_tuple)


r_nodes = random_nodes.copy()
r_nodes.remove(0)
r_nodes.remove(1)
r_nodes_iter = itertools.permutations(r_nodes)

min_rec_conns = list()
min_rec_conns_len = sys.maxsize
previous_graph_topologies = set()

t_start = time.time()

for permutation in r_nodes_iter:
    ordering = permutation + (1,)

    for graph_topology, graph_topology_tuple in create_groupings(ordering):
        if graph_topology_tuple in previous_graph_topologies:
            continue
        else:
            previous_graph_topologies.add(graph_topology_tuple)

        graph_topology.insert(0, {0})

        rec_conns = set()
        for conn in random_conns:
            conn_start_index = None
            conn_end_index = None

            for level_index in range(len(graph_topology)):
                if conn[0] in graph_topology[level_index]:
                    conn_start_index = level_index

                if conn[1] in graph_topology[level_index]:
                    conn_end_index = level_index

                if conn_start_index is not None and conn_end_index is not None:
                    break

            if conn_start_index >= conn_end_index:
                rec_conns.add((conn[0], conn[1]))

            if len(rec_conns) > min_rec_conns_len:
                break

        if len(rec_conns) < min_rec_conns_len:
            min_rec_conns = [(graph_topology, rec_conns)]
            min_rec_conns_len = len(rec_conns)
        elif len(rec_conns) == min_rec_conns_len:
            min_rec_conns.append((graph_topology, rec_conns))

t_end = time.time()

print(f"\nprocessing time: {t_end - t_start}")

print(f"\nmin_rec_conns: {min_rec_conns}")
print(f"len min_rec_conns: {len(min_rec_conns)}")

########################################################################################################################

min_graph_top_groupings = len(min(min_rec_conns, key=lambda x: len(x[0]))[0])

min_graph_min_rec_conns = list()
for min_rec_conn_item in min_rec_conns:
    if len(min_rec_conn_item[0]) == min_graph_top_groupings:
        min_graph_min_rec_conns.append(min_rec_conn_item)

print(f"\nmin_graph_min_rec_conns: {min_graph_min_rec_conns}")
print(f"len min_graph_min_rec_conns: {len(min_graph_min_rec_conns)}")
'''
########################################################################################################################
'''
# Create Digraph, setting name and graph orientaion
dot = Digraph(name='tempgraph', graph_attr={'rankdir': 'TB'})

# Traverse all bp graph genes, adding the nodes and edges to the graph
for conn in random_conns:
    dot.edge(str(conn[0]), str(conn[1]))

# Render created dot graph, optionally showing it
dot.render(filename='tempgraph', directory=tempfile.gettempdir(), view=True, cleanup=True, format='svg')
'''
########################################################################################################################

# previously calculated input for testing purposes
'''
node_dependencies = {3: {0, 2, 5, 7, 8}, 1: {0, 2, 3, 4, 6}, 5: {0, 2}, 8: {5}, 6: {0, 3}, 4: {3}, 7: {2, 5}, 2: {0, 5}}
min_graph_min_rec_conns = [([{0}, {2}, {5}, {8, 7}, {3}, {4, 6}, {1}], {(5, 2)}),
                            ([{0}, {5}, {2}, {8, 7}, {3}, {4, 6}, {1}], {(2, 5)}),
                            ([{0}, {5}, {8, 2}, {7}, {3}, {4, 6}, {1}], {(2, 5)})]
'''
node_dependencies = {3: {2, 4, 5, 7, 8}, 8: {4}, 2: {0, 3, 5}, 1: {0, 2, 3, 4}, 7: {2, 6}, 6: {3}, 4: {0, 2, 3},
                     5: {3, 6}}
min_graph_min_rec_conns = [([{0}, {6}, {5}, {2}, {4}, {8, 7}, {3}, {1}], {(3, 2), (3, 4), (3, 6), (3, 5)}),
                           ([{0}, {6}, {5}, {2}, {4, 7}, {8}, {3}, {1}], {(3, 2), (3, 4), (3, 6), (3, 5)})]

graph_topology, recurrent_conns = cyclic_toposort(node_dependencies=node_dependencies, start_node=0)

print(f"\nfinal graph_topology: {graph_topology}")
print(f"final recurrent_conns: {recurrent_conns}")

print(f"correct final graph topologies and recurrent conns: {min_graph_min_rec_conns}")
