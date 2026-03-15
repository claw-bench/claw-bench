"""Verifier for data-005: Outlier Detection Using IQR."""

from pathlib import Path
import csv
import json
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def analysis(workspace):
    path = workspace / "analysis.json"
    assert path.exists(), "analysis.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def outlier_rows(workspace):
    path = workspace / "outliers.csv"
    assert path.exists(), "outliers.csv not found"
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


def test_outliers_file_exists(workspace):
    assert (workspace / "outliers.csv").exists()


def test_analysis_file_exists(workspace):
    assert (workspace / "analysis.json").exists()


def test_outlier_count(analysis):
    assert analysis["outlier_count"] == 5, f"Expected 5 outliers, got {analysis['outlier_count']}"


def test_iqr_value(analysis):
    assert abs(analysis["iqr"] - 13.7) < 0.5, f"Expected IQR ~13.7, got {analysis['iqr']}"


def test_bounds_correct(analysis):
    assert abs(analysis["lower_bound"] - 24.1) < 1.0, f"Expected lower_bound ~24.1, got {analysis['lower_bound']}"
    assert abs(analysis["upper_bound"] - 78.9) < 1.0, f"Expected upper_bound ~78.9, got {analysis['upper_bound']}"


def test_all_true_outliers_found(outlier_rows):
    """The known outlier values (2.1, 3.5, 97.8, 99.2, 100.5) should all be detected."""
    found_values = [float(r["value"]) for r in outlier_rows]
    known_outliers = [2.1, 3.5, 97.8, 99.2, 100.5]
    for ov in known_outliers:
        assert any(abs(fv - ov) < 0.1 for fv in found_values), f"Known outlier {ov} not found in results"


def test_analysis_keys(analysis):
    for key in ["q1", "q3", "iqr", "lower_bound", "upper_bound", "outlier_count"]:
        assert key in analysis, f"Missing key: {key}"
