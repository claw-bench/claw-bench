"""Verifier for data-008: Pairwise Correlation Analysis."""

from pathlib import Path
import csv
import json
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def corr_rows(workspace):
    path = workspace / "correlations.csv"
    assert path.exists(), "correlations.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


@pytest.fixture
def top_corr(workspace):
    path = workspace / "top_correlations.json"
    assert path.exists(), "top_correlations.json not found"
    return json.loads(path.read_text())


def test_correlations_file_exists(workspace):
    assert (workspace / "correlations.csv").exists()


def test_top_correlations_file_exists(workspace):
    assert (workspace / "top_correlations.json").exists()


def test_matrix_is_symmetric(corr_rows):
    matrix = {r["variable"]: r for r in corr_rows}
    variables = [r["variable"] for r in corr_rows]
    for v1 in variables:
        for v2 in variables:
            a = float(matrix[v1][v2])
            b = float(matrix[v2][v1])
            assert abs(a - b) < 0.001, f"Matrix not symmetric: {v1},{v2} = {a} but {v2},{v1} = {b}"


def test_diagonal_is_one(corr_rows):
    for row in corr_rows:
        var = row["variable"]
        assert abs(float(row[var]) - 1.0) < 0.001, f"Diagonal for {var} should be 1.0, got {row[var]}"


def test_values_in_range(corr_rows):
    variables = [r["variable"] for r in corr_rows]
    for row in corr_rows:
        for v in variables:
            val = float(row[v])
            assert -1.0 <= val <= 1.0, f"Correlation out of range: {row['variable']},{v} = {val}"


def test_top_3_count(top_corr):
    assert len(top_corr) == 3, f"Expected 3 top correlations, got {len(top_corr)}"


def test_top_3_sorted_by_abs(top_corr):
    abs_vals = [abs(p["correlation"]) for p in top_corr]
    assert abs_vals == sorted(abs_vals, reverse=True), "Top correlations not sorted by absolute value"


def test_top_pairs_reasonable(top_corr):
    expected = [{"var1": "age", "var2": "income", "correlation": 0.9379}, {"var1": "height", "var2": "weight", "correlation": 0.6148}, {"var1": "height", "var2": "score", "correlation": 0.182}]
    for i, pair in enumerate(top_corr):
        exp = expected[i]
        pair_set = {pair["var1"], pair["var2"]}
        exp_set = {exp["var1"], exp["var2"]}
        assert pair_set == exp_set, f"Top pair {i+1}: expected {exp_set}, got {pair_set}"
        assert abs(pair["correlation"] - exp["correlation"]) < 0.05, f"Top pair {i+1}: correlation mismatch"
