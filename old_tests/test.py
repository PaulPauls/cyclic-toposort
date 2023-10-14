ff_node_inputs = {
    1: {2, 3, 4, 5, 38, 55, 106},
    2: set(),
    3: {140},
    4: {97},
    5: set(),
    55: {3},
    26: {180, 55},
    114: {26},
    180: {4},
    140: {616, 180},
    38: set(),
    97: {106},
    106: {55},
    616: set(),
}


def check_feedforward_topology(node_inputs) -> bool:
    """"""
    while True:
        dependencyless = set()
        for node, incomings in node_inputs.items():
            if len(incomings) == 0:
                dependencyless.add(node)

        if not dependencyless:
            return False

        for node in dependencyless:
            del node_inputs[node]

        if not node_inputs:
            break

        for incomings in node_inputs.values():
            incomings -= dependencyless

    return True


node_inputs = {k: v.copy() for k, v in ff_node_inputs.items()}
print(node_inputs)
print(check_feedforward_topology(node_inputs))

# Set 107 as still recurrent and remove
node_inputs = {k: v.copy() for k, v in ff_node_inputs.items()}
node_inputs[106].remove(55)
print(node_inputs)
print(check_feedforward_topology(node_inputs))

# Set 542 as still recurrent and remove
node_inputs = {k: v.copy() for k, v in ff_node_inputs.items()}
node_inputs[140].remove(180)
print(node_inputs)
print(check_feedforward_topology(node_inputs))

# Set both 107 and 542 as still recurrent and remove
node_inputs = {k: v.copy() for k, v in ff_node_inputs.items()}
node_inputs[106].remove(55)
node_inputs[140].remove(180)
print(node_inputs)
print(check_feedforward_topology(node_inputs))
