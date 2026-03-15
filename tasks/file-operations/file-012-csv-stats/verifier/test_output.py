"""Verifier for file-012: CSV Column Extraction and Statistics."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def stats(workspace):
    """Read and parse the stats.json file."""
    path = workspace / "stats.json"
    assert path.exists(), "stats.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """stats.json must exist in the workspace."""
    assert (workspace / "stats.json").exists()


def test_valid_json(workspace):
    """stats.json must be valid JSON."""
    path = workspace / "stats.json"
    text = path.read_text()
    try:
        json.loads(text)
    except json.JSONDecodeError as e:
        pytest.fail(f"stats.json is not valid JSON: {e}")


def test_has_all_keys(stats):
    """stats.json must contain min, max, mean, and median keys."""
    for key in ["min", "max", "mean", "median"]:
        assert key in stats, f"Missing key '{key}' in stats.json"


def test_values_are_numbers(stats):
    """All values must be numbers (int or float), not strings."""
    for key in ["min", "max", "mean", "median"]:
        assert isinstance(stats[key], (int, float)), (
            f"Value for '{key}' should be a number, got {type(stats[key]).__name__}"
        )


def test_correct_min(stats):
    """Minimum price should be 8.75."""
    assert abs(stats["min"] - 8.75) < 0.01, (
        f"Expected min=8.75, got {stats['min']}"
    )


def test_correct_max(stats):
    """Maximum price should be 89.99."""
    assert abs(stats["max"] - 89.99) < 0.01, (
        f"Expected max=89.99, got {stats['max']}"
    )


def test_correct_mean(stats):
    """Mean price should be approximately 41.78."""
    assert abs(stats["mean"] - 41.78) < 0.01, (
        f"Expected mean~41.78, got {stats['mean']}"
    )


def test_correct_median(stats):
    """Median price should be approximately 39.88."""
    assert abs(stats["median"] - 39.88) < 0.01, (
        f"Expected median~39.88, got {stats['median']}"
    )
