#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import json
import numpy as np
from scipy.optimize import linprog

# Load problem
with open(f"{WORKSPACE}/optimization_problem.json") as f:
    problem = json.load(f)

Q = np.array(problem["Q"])
c = np.array(problem["c"])
constraints = problem["constraints"]

n = len(c)

# Extract constraints A x <= b
A = np.array([constr["A"] for constr in constraints])
b = np.array([constr["b"] for constr in constraints])

# Parameters
max_iter = 1000
tol = 1e-6
alpha = 1e-2  # step size

# Initial point
x = np.zeros(n)

# Precompute for efficiency
Qx = lambda x: Q.dot(x)
obj = lambda x: 0.5 * x.dot(Q.dot(x)) + c.dot(x)
grad = lambda x: Q.dot(x) + c

convergence_history = []

# Projection function: project y onto feasible set {x | A x <= b}
# We solve the QP: min_{z} 0.5||z - y||^2 s.t. A z <= b
# This is a quadratic program with identity quadratic term and linear constraints

def project(y):
    # linprog solves linear programs, but we need a QP projection
    # We'll solve the QP via scipy.optimize.minimize with constraints
    from scipy.optimize import minimize

    def objective(z):
        return 0.5 * np.sum((z - y)**2)

    cons = [{'type': 'ineq', 'fun': lambda z, A_i=A[i], b_i=b[i]: b_i - np.dot(A_i, z)} for i in range(len(b))]

    res = minimize(objective, y, constraints=cons, method='SLSQP', options={'ftol':1e-9, 'disp': False, 'maxiter': 1000})
    if not res.success:
        # fallback: return previous point
        return y
    return res.x

prev_obj = obj(x)
convergence_history.append(prev_obj)

for iteration in range(1, max_iter + 1):
    g = grad(x)
    y = x - alpha * g
    x = project(y)
    curr_obj = obj(x)
    convergence_history.append(curr_obj)
    if abs(curr_obj - prev_obj) < tol:
        break
    prev_obj = curr_obj

result = {
    "solution": x.tolist(),
    "objective_value": float(curr_obj),
    "iterations": iteration,
    "convergence_history": convergence_history[1:]  # exclude initial obj
}

with open(f"{WORKSPACE}/optimization_result.json", "w") as f:
    json.dump(result, f, indent=2)
EOF
