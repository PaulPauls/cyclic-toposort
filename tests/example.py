import cyclic_toposort as ct

cyclic_graph_edges = {(1, 2), (2, 3), (3, 5), (3, 6), (4, 1), (4, 5), (4, 6), (5, 2), (5, 7), (6, 1), (8, 6)}
result = ct.cyclic_toposort(cyclic_graph_edges)
print(result)

result = ct.cyclic_toposort(cyclic_graph_edges, start_node=2)
print(result)

acyclic_graph_edges = {(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (5, 3), (5, 6), (7, 6)}
result = ct.acyclic_toposort(acyclic_graph_edges)
print(result)
