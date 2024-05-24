# From Brian Sahach's post
import pulp
import numpy as np

# sample data: 3 Decision-making units (DMUs) with two inputs each and single output
inputs = np.array([[2,5]], [4,3], [6,4]])
outputs = np.array([100, 125, 120])

# Calculate efficiencies of each DMU using DEA with linear programming
efficiencies =[]
for di in range(len(inputs)):
  prob = pulp.LpProblem("DEA", pulp.LPMaximize)
  w_in = pulp.LpVariable.dicts("w_in", range(2), lowBound = 0)
  w_out = pulp.LpVariable("w_out", lowBound = 0)
  prob += w_out * outputs[di] - sum(w_in[i] * inputs[di][i] for i in range (2))

  # Add constraints to ensure no DMU's efficiency exceeds 1
  for i in range(len(inputs)):
    prob += w_out * outputs[i] - sum(w_in[j] * inputs[i][j] for j in range(2)) <= 1
  
  prob.solve()
  efficiencies.append(min(pulp.value(prob.objective), 1) if prob.status == 1 else None)

for i, eff in enumerate(efficiencies):
  print("Efficiency of DMU " + chr(65 + i) + ": " + str(eff)
