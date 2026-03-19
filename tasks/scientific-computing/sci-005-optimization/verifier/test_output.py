import json
import os
from pathlib import Path
import pytest
import numpy as np

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_solution_file_exists(workspace):
    result_file = workspace / "optimization_result.json"
    assert result_file.exists(), "Result file optimization_result.json not found"

@pytest.mark.weight(5)
def test_solution_format_and_values(workspace):
    result_file = workspace / "optimization_result.json"
    with open(result_file) as f:
        result = json.load(f)

    # Check keys
    for key in ["solution", "objective_value", "iterations", "convergence_history"]:
        assert key in result, f"Missing key '{key}' in result"

    solution = result["solution"]
    obj_val = result["objective_value"]
    iterations = result["iterations"]
    conv_hist = result["convergence_history"]

    # solution should be list of floats of length 5
    assert isinstance(solution, list), "Solution should be a list"
    assert len(solution) == 5, f"Solution length expected 5, got {len(solution)}"
    assert all(isinstance(x, (int, float)) for x in solution), "All solution elements must be numbers"

    # objective_value should be float
    assert isinstance(obj_val, (int, float)), "objective_value must be a number"

    # iterations should be int and between 1 and 1000
    assert isinstance(iterations, int), "iterations must be int"
    assert 1 <= iterations <= 1000, "iterations out of expected range"

    # convergence_history should be list of floats with length equal to iterations
    assert isinstance(conv_hist, list), "convergence_history must be a list"
    assert len(conv_hist) == iterations, "convergence_history length must equal iterations"
    assert all(isinstance(v, (int, float)) for v in conv_hist), "convergence_history elements must be numbers"

@pytest.mark.weight(7)
def test_objective_decreases_and_constraints_satisfied(workspace):
    # Load problem
    problem_file = workspace / "optimization_problem.json"
    with open(problem_file) as f:
        problem = json.load(f)

    Q = np.array(problem["Q"])
    c = np.array(problem["c"])
    constraints = problem["constraints"]

    # Load result
    result_file = workspace / "optimization_result.json"
    with open(result_file) as f:
        result = json.load(f)

    x = np.array(result["solution"])
    conv_hist = result["convergence_history"]

    # Check objective decreases monotonically
    for i in range(1, len(conv_hist)):
        assert conv_hist[i] <= conv_hist[i-1] + 1e-8, f"Objective did not decrease at iteration {i}"

    # Check constraints A_i x <= b_i
    for constr in constraints:
        A_i = np.array(constr["A"])
        b_i = constr["b"]
        val = np.dot(A_i, x)
        assert val <= b_i + 1e-6, f"Constraint violated: {val} > {b_i}"

    # Check objective_value matches computed value within tolerance
    obj_val_reported = result["objective_value"]
    obj_val_calc = 0.5 * x.dot(Q.dot(x)) + c.dot(x)
    assert abs(obj_val_reported - obj_val_calc) < 1e-5, "Reported objective_value does not match computed value"
