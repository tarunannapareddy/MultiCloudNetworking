import pulp

# Create the problem
prob = pulp.LpProblem("Shortest_Path_Problem", pulp.LpMinimize)

# Define capacities and demands
capacities = {('A','B'): 2,
              ('B','C'): 4,
              ('D','C'): 2,
              ('D','B'): 2}

costs = {('A','B'): 0,
              ('B','C'): 0,
              ('D','C'): 0,
              ('D','B'): 0}

demands = {('A', 'C'): 2, ('D', 'C'):4}

# Extract nodes and links from capacities
nodes = set()
links = set()
for link in capacities:
    nodes.add(link[0])
    nodes.add(link[1])
    links.add(link)

# Create variables
vars = pulp.LpVariable.dicts("Route", ((p, i, j) for p in demands for i, j in links),
                             lowBound=0,
                             upBound=1,
                             cat='Continuous')

alpha = 1
beta = 0 
M =1000
# Objective function
#prob += pulp.lpSum([alpha * vars[(d, i, j)] * demands[d] for d, i, j in vars]), "Minimize_congestion"

obj_terms = []
for (i,j) in links:
    for (k,l) in links:
        if (i,j) != (k,l):
            demand1 = pulp.lpSum([vars[(d,i,j)] * demands[d] for d in demands])
            demand2 = pulp.lpSum([vars[(d,k,l)] * demands[d] for d in demands]) 
            obj_terms.append(demand1 - demand2 + M)  
            
prob += pulp.lpSum(obj_terms), "Minimize_demand_difference"

# Constraints
for p in demands:
    for n in nodes:
        if n == p[0]:
            prob += pulp.lpSum(vars[p, i, j] for i, j in links if i == n) - pulp.lpSum(vars[p, i, j] for i, j in links if j == n) == 1
        elif n == p[1]:
            prob += pulp.lpSum(vars[p, i, j] for i, j in links if i == n) - pulp.lpSum(vars[p, i, j] for i, j in links if j == n) == -1
        else:
            prob += pulp.lpSum(vars[p, i, j] for i, j in links if i == n) - pulp.lpSum(vars[p, i, j] for i, j in links if j == n) == 0

for i,j in links:
    capacity = capacities.get((i, j), -1)
    if(capacity >0):
        prob += pulp.lpSum([vars[(d,i,j)] * demands[d] for d in demands]) <= capacity

# Solve the problem
status = prob.solve()

# Check solution satisfaction
solution_satisfied = True
for i, j in links:
    print(i,j,sum(vars[(d, i, j)].varValue * demands[d] for d in demands), capacities.get((i, j), -1) )
    if sum(vars[(d, i, j)].varValue * demands[d] for d in demands) > capacities.get((i, j), -1):
        solution_satisfied = False
        break

# Print results
if solution_satisfied:
    print("Solution satisfied.")
    for p in demands:
        print(f"\nRoutes for demand {p}:")
        for i, j in links:
            if vars[p, i, j].varValue > 0:
                print(f"  Uses link {i} -> {j} and capacity split {vars[p, i, j].varValue}")
else:
    print("Solution not satisfied.")