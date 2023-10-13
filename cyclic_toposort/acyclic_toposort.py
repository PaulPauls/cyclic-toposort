"""Module providing functions for sorting directed acyclic graphs."""

# Copyright (c) 2020 Paul Pauls.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


def acyclic_toposort(edges) -> [{int}]:
    """Create topological sorting of an acyclic graph with maximized groupings of levels. Return this topological
    sorting as list of sets that represent each topological level beginning with the start (= dependencyless) nodes of
    the acyclic graph.
    :param edges: iterable of 2-tuples, specifying start and end for each edge
    :return: topological sorting of graph as list of sets that represent each topological level beginning with the start
             nodes.
    """
    # Create python dict that associates each node with the set of all nodes that having an incoming edge (node_ins) to
    # that particular node. If a node has no incoming connections will the node be associated with an empty set.
    node_ins = {}
    for edge_start, edge_end in edges:
        # Don't consider cyclic node edges as not relevant for topological sorting
        if edge_start == edge_end:
            continue

        if edge_start not in node_ins:
            node_ins[edge_start] = set()

        if edge_end not in node_ins:
            node_ins[edge_end] = {edge_start}
        else:
            node_ins[edge_end].add(edge_start)

    graph_topology = []

    while True:
        # Determine all nodes having no input/dependency in the current topological level
        dependencyless = set()
        for node, incomings in node_ins.items():
            if len(incomings) == 0:
                dependencyless.add(node)

        if not dependencyless:
            if not node_ins:
                msg = "Invalid graph detected"
                raise RuntimeError(msg)
            else:
                msg = "Cyclic graph detected in acyclic_toposort function"
                raise RuntimeError(msg)

        # Set dependencyless nodes as the nodes of the next topological level
        graph_topology.append(dependencyless)

        # Remove dependencyless nodes from node_ins collection, as those dependencyless nodes have been placed.
        for node in dependencyless:
            del node_ins[node]

        # If all nodes are placed, exit topological sorting
        if not node_ins:
            break

        # Remove depdencyless nodes from node_ins (the set of required incoming nodes) as those dependencyless nodes
        # have been placed and their dependency to other nodes is therefore fulfilled
        for node, incomings in node_ins.items():
            node_ins[node] = incomings - dependencyless

    return graph_topology
