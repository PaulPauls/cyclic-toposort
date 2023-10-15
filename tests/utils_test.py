"""Tests for the utils module."""

from cyclic_toposort.utils import generate_reduced_ins_outs


def test_basic_functionality() -> None:
    """Test basic functionality of generate_reduced_ins_outs() with a small graph."""
    edges = {(1, 3), (2, 3), (3, 4)}
    node_ins: dict[int, set[int]] = {1: set(), 2: set(), 3: {1, 2}, 4: {3}}
    node_outs: dict[int, set[int]] = {1: {3}, 2: {3}, 3: {4}, 4: set()}

    results = list(generate_reduced_ins_outs(edges=edges, node_ins=node_ins, node_outs=node_outs))
    expected = [
        ({1: set(), 2: set(), 3: {1}, 4: {3}}, {1: {3}, 2: set(), 3: {4}, 4: set()}, {(2, 3)}),
        ({1: set(), 2: set(), 3: {2}, 4: {3}}, {1: set(), 2: {3}, 3: {4}, 4: set()}, {(1, 3)}),
        ({1: set(), 2: set(), 3: {1, 2}, 4: set()}, {1: {3}, 2: {3}, 3: set(), 4: set()}, {(3, 4)}),
        ({1: set(), 2: set(), 3: set(), 4: {3}}, {1: set(), 2: set(), 3: {4}, 4: set()}, {(2, 3), (1, 3)}),
        ({1: set(), 2: set(), 3: {1}, 4: set()}, {1: {3}, 2: set(), 3: set(), 4: set()}, {(2, 3), (3, 4)}),
        ({1: set(), 2: set(), 3: {2}, 4: set()}, {1: set(), 2: {3}, 3: set(), 4: set()}, {(1, 3), (3, 4)}),
        ({1: set(), 2: set(), 3: set(), 4: set()}, {1: set(), 2: set(), 3: set(), 4: set()}, {(2, 3), (1, 3), (3, 4)}),
    ]

    assert results == expected


def test_empty_edges() -> None:
    """Make sure the function works with empty edges."""
    edges: set[tuple[int, int]] = set()
    node_ins: dict[int, set[int]] = {}
    node_outs: dict[int, set[int]] = {}

    results = list(generate_reduced_ins_outs(edges=edges, node_ins=node_ins, node_outs=node_outs))

    assert results == []


def test_input_not_modified() -> None:
    """Make sure the input dictionaries are not modified after calling the function."""
    edges = {(1, 2), (2, 3), (3, 5), (3, 6), (4, 1), (4, 5), (4, 6), (5, 2), (5, 7), (6, 1), (8, 6)}
    node_ins: dict[int, set[int]] = {1: {4, 6}, 2: {1, 5}, 3: {2}, 4: set(), 5: {3, 4}, 6: {3, 4, 8}, 7: {5}, 8: set()}
    node_outs: dict[int, set[int]] = {1: {2}, 2: {3}, 3: {5, 6}, 4: {1, 5, 6}, 5: {2, 7}, 6: {1}, 7: set(), 8: {6}}

    _ = list(generate_reduced_ins_outs(edges=edges, node_ins=node_ins, node_outs=node_outs))

    assert node_ins == {1: {4, 6}, 2: {1, 5}, 3: {2}, 4: set(), 5: {3, 4}, 6: {3, 4, 8}, 7: {5}, 8: set()}
    assert node_outs == {1: {2}, 2: {3}, 3: {5, 6}, 4: {1, 5, 6}, 5: {2, 7}, 6: {1}, 7: set(), 8: {6}}
