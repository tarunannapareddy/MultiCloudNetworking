import pulp

def solve_shortest_path_problem(registered_nodes, registered_attachments, demands):
    # Extract nodes and links from registered_nodes and registered_attachments
    nodes = set(registered_nodes.keys())
    links = set()
    capacities = {}
    for attachment in registered_attachments:
        src_node = attachment['srcNodeName']
        dst_node = attachment['dstNodeName']
        capacity = attachment['capacity']
        links.add((src_node, dst_node))
        capacities[(src_node, dst_node)] = capacity

    # Create the problem
    prob = pulp.LpProblem("Shortest_Path_Problem", pulp.LpMinimize)

    # Create variables
    vars = pulp.LpVariable.dicts("Route", ((p, i, j) for p in demands for i, j in links), lowBound=0, upBound=1, cat='Continuous')

    # Objective function (minimize the maximum link utilization)
    obj_terms = []
    for (i, j) in links:
        demand_sum = pulp.lpSum([vars[(d, i, j)] * demands[d] for d in demands])
        obj_terms.append(demand_sum / capacities[(i, j)])
    prob += pulp.lpSum(obj_terms), "Minimize_max_link_utilization"

    # Constraints
    for p in demands:
        for n in nodes:
            if n == p[0]:
                prob += pulp.lpSum(vars[p, i, j] for i, j in links if i == n) - pulp.lpSum(vars[p, i, j] for i, j in links if j == n) == 1
            elif n == p[1]:
                prob += pulp.lpSum(vars[p, i, j] for i, j in links if i == n) - pulp.lpSum(vars[p, i, j] for i, j in links if j == n) == -1
            else:
                prob += pulp.lpSum(vars[p, i, j] for i, j in links if i == n) - pulp.lpSum(vars[p, i, j] for i, j in links if j == n) == 0

    for i, j in links:
        capacity = capacities[(i, j)]
        prob += pulp.lpSum([vars[(d, i, j)] * demands[d] for d in demands]) <= capacity

    # Solve the problem
    status = prob.solve()

    # Extract the routing paths
    routing_paths = []
    if status == pulp.LpStatusOptimal:
        for p in demands:
            for i, j in links:
                if vars[p, i, j].varValue > 0:
                    routing_paths.append((i, j, vars[p, i, j].varValue * demands[p]))

    return routing_paths