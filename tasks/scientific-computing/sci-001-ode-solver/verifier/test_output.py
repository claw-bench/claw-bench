import os
from pathlib import Path
import json
import csv
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_equilibrium_json(workspace):
    eq_file = workspace / "equilibrium.json"
    assert eq_file.exists(), "equilibrium.json file is missing"
    data = json.load(eq_file.open())
    # Expected equilibrium
    expected_prey = 0.4 / 0.1  # c/d = 4.0
    expected_predator = 1.1 / 0.4  # a/b = 2.75
    assert "prey" in data and "predator" in data, "Missing keys in equilibrium.json"
    assert abs(data["prey"] - expected_prey) < 1e-6, f"Prey equilibrium incorrect: {data['prey']}"
    assert abs(data["predator"] - expected_predator) < 1e-6, f"Predator equilibrium incorrect: {data['predator']}"

@pytest.mark.weight(7)
def test_simulation_csv(workspace):
    csv_file = workspace / "simulation.csv"
    assert csv_file.exists(), "simulation.csv file is missing"

    with csv_file.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Check header
    assert reader.fieldnames == ["t", "prey", "predator"], "CSV headers incorrect"

    # Check number of rows (should be 1 + (50/0.01) = 5001)
    assert len(rows) == 5001, f"Expected 5001 rows, got {len(rows)}"

    # Check initial conditions
    first = rows[0]
    assert abs(float(first["t"]) - 0.0) < 1e-8
    assert abs(float(first["prey"]) - 10.0) < 1e-8
    assert abs(float(first["predator"]) - 10.0) < 1e-8

    # Check final time
    last = rows[-1]
    assert abs(float(last["t"]) - 50.0) < 1e-8

    # Spot check a few values for sanity (values should be positive and reasonable)
    for row in rows[::1000]:  # every 1000th step
        t = float(row["t"])
        prey = float(row["prey"])
        predator = float(row["predator"])
        assert prey > 0, f"Prey population not positive at t={t}"
        assert predator > 0, f"Predator population not positive at t={t}"

@pytest.mark.weight(10)
def test_numerical_solution_behavior(workspace):
    csv_file = workspace / "simulation.csv"
    with csv_file.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Extract prey and predator arrays
    prey_vals = [float(r["prey"]) for r in rows]
    predator_vals = [float(r["predator"]) for r in rows]

    # The populations should oscillate roughly around equilibrium
    # Check that prey and predator values cross their equilibrium values multiple times
    prey_eq = 0.4 / 0.1  # 4.0
    pred_eq = 1.1 / 0.4  # 2.75

    def count_crossings(values, level):
        crossings = 0
        for i in range(1, len(values)):
            if (values[i-1] - level) * (values[i] - level) < 0:
                crossings += 1
        return crossings

    prey_crossings = count_crossings(prey_vals, prey_eq)
    pred_crossings = count_crossings(predator_vals, pred_eq)

    assert prey_crossings >= 3, f"Prey population does not oscillate enough: {prey_crossings} crossings"
    assert pred_crossings >= 3, f"Predator population does not oscillate enough: {pred_crossings} crossings"
