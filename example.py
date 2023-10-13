import cyclic_toposort as ct

edges = {(0, 1), (1, 2), (2, 3), (3, 0)}
result = ct.cyclic_toposort(edges, start_node=1)

# edges = {(1, 2), (2, 3), (3, 5), (3, 6), (4, 1), (4, 5), (4, 6), (5, 2), (5, 7), (6, 1), (8, 6)}
# result = ct.cyclic_toposort(edges, start_node=1)

print(result)
