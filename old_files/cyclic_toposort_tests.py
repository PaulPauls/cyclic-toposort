from cyclic_toposort import cyclic_toposort


def test_acyclic_graph():
    edges = {(1, 2), (2, 3), (3, 4)}
    result = cyclic_toposort(edges)
    assert result == ([{1}, {2}, {3}, {4}], set())


def test_cyclic_graph():
    edges = {(1, 2), (2, 3), (3, 1)}
    result = cyclic_toposort(edges)
    cyclic_edges = result[1]
    assert cyclic_edges == {(2, 3)}


def test_self_loop():
    edges = {(1, 1), (1, 2), (2, 3)}
    result = cyclic_toposort(edges)
    assert result == ([{1}, {2}, {3}], set())


def test_start_node():
    edges = {(1, 2), (2, 3), (3, 1), (3, 4)}
    result = cyclic_toposort(edges, start_node=3)
    cyclic_edges = result[1]
    assert cyclic_edges


def test_recursive_call():
    edges = {(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)}
    result = cyclic_toposort(edges)
    cyclic_edges = result[1]
    assert len(cyclic_edges) > 0
