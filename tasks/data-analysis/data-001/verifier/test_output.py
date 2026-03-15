"""Verifier for data-001: Basic Statistics Computation."""

from pathlib import Path
import json
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def stats(workspace):
    path = workspace / "stats.json"
    assert path.exists(), "stats.json not found in workspace"
    return json.loads(path.read_text())


def test_stats_file_exists(workspace):
    assert (workspace / "stats.json").exists()


def test_mean_correct(stats):
    assert abs(stats["mean"] - 45.8) < 0.01, f"Expected mean ~45.8, got {stats['mean']}"


def test_median_correct(stats):
    assert abs(stats["median"] - 43.5) < 0.01, f"Expected median ~43.5, got {stats['median']}"


def test_mode_correct(stats):
    assert stats["mode"] == 42, f"Expected mode 42, got {stats['mode']}"


def test_std_dev_correct(stats):
    assert abs(stats["std_dev"] - 19.56) < 0.01, f"Expected std_dev ~19.56, got {stats['std_dev']}"


def test_all_keys_present(stats):
    for key in ["mean", "median", "mode", "std_dev"]:
        assert key in stats, f"Missing key: {key}"
