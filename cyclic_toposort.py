def cyclic_toposort(node_dependencies, start_node):
    """"""
    node_deps = node_dependencies.copy()
    node_deps[0] = set()

    graph_topology = list()
    recurrent_conns = set()

    while True:
        print(f"\ngraph_topology: {graph_topology}")
        print(f"recurrent_conns: {recurrent_conns}")
        print(f"node_deps: {node_deps}")

        # find all nodes in graph having no dependencies in current iteration
        dependencyless = set()
        for node, dep in node_deps.items():
            if len(dep) == 0:
                dependencyless.add(node)

        # Recurrency detected
        if not dependencyless:

            cyclic_deps = node_deps.copy()
            cyclic_deps_occurences = dict()
            for node in cyclic_deps.keys():
                cyclic_deps_occurences[node] = {node}

            cyclic_node = None
            while cyclic_node is None:
                for node, deps in cyclic_deps.items():
                    cyclic_deps_occurences[node] = cyclic_deps_occurences[node].union(deps)

                    new_deps = set()
                    for dep in deps:
                        new_deps = new_deps.union(node_deps[dep])
                    new_deps = new_deps - cyclic_deps_occurences[node]
                    if not new_deps:
                        cyclic_node = node
                        break

                    cyclic_deps[node] = new_deps

            # Set all required dependencies of determined cyclic node as recurrent
            for dep in node_deps[cyclic_node]:
                recurrent_conns.add((dep, cyclic_node))

            dependencyless.add(cyclic_node)

        # Add dependencyless nodes of current generation to list
        graph_topology.append(dependencyless)

        # remove keys with empty dependencies and remove all nodes that are considered dependencyless from the
        # dependencies of other nodes in order to create next iteration
        for node in dependencyless:
            del node_deps[node]

        # if all nodes were removed from dependency list, exit topological sorting
        if not node_deps:
            break

        for node, dependencies in node_deps.items():
            node_deps[node] = dependencies - dependencyless

    return graph_topology, recurrent_conns
