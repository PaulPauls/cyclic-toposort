import pytest

from cyclic_toposort import acyclic_toposort


def test_single_level_graph():
    edges = [(1, 2), (3, 4)]
    result = acyclic_toposort(edges)
    expected = [{1, 3}, {2, 4}]
    assert result == expected


def test_multi_level_graph():
    edges = [(1, 2), (2, 3), (4, 5), (5, 3)]
    result = acyclic_toposort(edges)
    expected = [{1, 4}, {2, 5}, {3}]
    assert result == expected


def test_cyclic_graph():
    edges = [(1, 2), (2, 3), (3, 1)]
    with pytest.raises(RuntimeError, match="Cyclic graph detected"):
        acyclic_toposort(edges)


def test_empty_graph():
    edges = []
    with pytest.raises(RuntimeError, match="Invalid graph detected"):
        acyclic_toposort(edges)


def test_self_referential_edges():
    edges = [(1, 2), (2, 2), (3, 4)]
    result = acyclic_toposort(edges)
    expected = [{1, 3}, {2, 4}]
    assert result == expected
