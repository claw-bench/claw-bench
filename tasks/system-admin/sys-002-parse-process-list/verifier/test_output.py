"""Verifier for sys-002: Parse Process List."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the top_processes.json contents."""
    path = workspace / "top_processes.json"
    assert path.exists(), "top_processes.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """top_processes.json must exist in the workspace."""
    assert (workspace / "top_processes.json").exists()


def test_total_processes_count(report):
    """total_processes must equal 15 (the number of process lines)."""
    assert report["total_processes"] == 15


def test_top_5_count(report):
    """top_5_cpu must have exactly 5 entries."""
    assert len(report["top_5_cpu"]) == 5


def test_top_process_is_ml_training(report):
    """The highest CPU process should be the ML training script (45.2%)."""
    top = report["top_5_cpu"][0]
    assert top["cpu_percent"] == pytest.approx(45.2, abs=0.5)
    assert "ml_training" in top["command"] or "python" in top["command"].lower()
