from cyclic_toposort.utils import generate_reduced_ins_outs


def test_basic_functionality():
    edges = {(1, 2), (2, 3)}
    node_ins = {1: set(), 2: {1}, 3: {2}}
    node_outs = {1: {2}, 2: {3}, 3: set()}

    results = list(generate_reduced_ins_outs(edges, node_ins, node_outs))
    expected = [
        ({1: set(), 2: set(), 3: {2}}, {1: set(), 2: {3}, 3: set()}, {(1, 2)}),
        ({1: set(), 2: {1}, 3: set()}, {1: {2}, 2: set(), 3: set()}, {(2, 3)}),
        ({1: set(), 2: set(), 3: set()}, {1: set(), 2: set(), 3: set()}, {(1, 2), (2, 3)}),
    ]

    assert results == expected


def test_empty_edges():
    edges = set()
    node_ins = {1: set(), 2: {1}, 3: {2}}
    node_outs = {1: {2}, 2: {3}, 3: set()}

    results = list(generate_reduced_ins_outs(edges, node_ins, node_outs))
    assert results == []


def test_input_not_modified():
    edges = {(1, 2), (2, 3)}
    node_ins = {1: set(), 2: {1}, 3: {2}}
    node_outs = {1: {2}, 2: {3}, 3: set()}

    _ = list(generate_reduced_ins_outs(edges, node_ins, node_outs))

    # Make sure the input dictionaries are not modified after calling the function
    assert node_ins == {1: set(), 2: {1}, 3: {2}}
    assert node_outs == {1: {2}, 2: {3}, 3: set()}
