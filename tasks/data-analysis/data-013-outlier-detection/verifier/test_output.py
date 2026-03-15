"""Verifier for data-013: Outlier Detection Report."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Read and parse outlier_report.json."""
    path = workspace / "outlier_report.json"
    assert path.exists(), "outlier_report.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """outlier_report.json must exist in the workspace."""
    assert (workspace / "outlier_report.json").exists()


def test_top_level_keys(report):
    """Report must contain all required top-level keys."""
    required = {"total_records", "outlier_count", "outliers", "summary_by_sensor"}
    assert required.issubset(report.keys()), f"Missing keys: {required - report.keys()}"


def test_total_records(report):
    """Total records must equal the number of rows in the CSV (36)."""
    assert report["total_records"] == 36


def test_outlier_count_matches_list(report):
    """outlier_count must match the length of the outliers list."""
    assert report["outlier_count"] == len(report["outliers"])


def test_outlier_count_is_correct(report):
    """There should be exactly 5 outliers in this dataset."""
    assert report["outlier_count"] == 5, f"Expected 5 outliers, got {report['outlier_count']}"


def test_outlier_structure(report):
    """Each outlier must have sensor_id, timestamp, value, z_score."""
    for o in report["outliers"]:
        assert "sensor_id" in o
        assert "timestamp" in o
        assert "value" in o
        assert "z_score" in o
        assert isinstance(o["z_score"], (int, float))


def test_known_outlier_values(report):
    """Known outlier values must be present in the outliers list."""
    outlier_values = {(o["sensor_id"], o["value"]) for o in report["outliers"]}
    # TEMP-01: 55.0 and -5.0 are outliers
    assert ("TEMP-01", 55.0) in outlier_values, "TEMP-01 value 55.0 should be an outlier"
    assert ("TEMP-01", -5.0) in outlier_values, "TEMP-01 value -5.0 should be an outlier"
    # HUM-01: 95.0 and 10.0 are outliers
    assert ("HUM-01", 95.0) in outlier_values, "HUM-01 value 95.0 should be an outlier"
    assert ("HUM-01", 10.0) in outlier_values, "HUM-01 value 10.0 should be an outlier"
    # PRES-01: 1050.0 is an outlier
    assert ("PRES-01", 1050.0) in outlier_values, "PRES-01 value 1050.0 should be an outlier"


def test_outliers_sorted_by_abs_z_score(report):
    """Outliers must be sorted by absolute z-score in descending order."""
    z_scores = [abs(o["z_score"]) for o in report["outliers"]]
    assert z_scores == sorted(z_scores, reverse=True), "Outliers not sorted by absolute z-score descending"


def test_summary_by_sensor_keys(report):
    """summary_by_sensor must contain all three sensors."""
    assert "TEMP-01" in report["summary_by_sensor"]
    assert "HUM-01" in report["summary_by_sensor"]
    assert "PRES-01" in report["summary_by_sensor"]


def test_summary_sensor_structure(report):
    """Each sensor summary must have required fields."""
    required = {"total_readings", "outlier_count", "mean", "std", "q1", "q3"}
    for sid, summary in report["summary_by_sensor"].items():
        assert required.issubset(summary.keys()), f"{sid} missing keys: {required - summary.keys()}"


def test_summary_sensor_readings_count(report):
    """Each sensor has 12 readings."""
    for sid, summary in report["summary_by_sensor"].items():
        assert summary["total_readings"] == 12, f"{sid} should have 12 readings"


def test_summary_sensor_outlier_counts(report):
    """TEMP-01 has 2 outliers, HUM-01 has 2, PRES-01 has 1."""
    s = report["summary_by_sensor"]
    assert s["TEMP-01"]["outlier_count"] == 2
    assert s["HUM-01"]["outlier_count"] == 2
    assert s["PRES-01"]["outlier_count"] == 1


def test_z_scores_are_rounded(report):
    """z_score values should be rounded to 2 decimal places."""
    for o in report["outliers"]:
        z_str = str(o["z_score"])
        if "." in z_str:
            decimals = len(z_str.split(".")[1])
            assert decimals <= 2, f"z_score {o['z_score']} has more than 2 decimal places"
