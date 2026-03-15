"""Verifier for sys-004: Log Analysis."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the log_analysis.json contents."""
    path = workspace / "log_analysis.json"
    assert path.exists(), "log_analysis.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """log_analysis.json must exist in the workspace."""
    assert (workspace / "log_analysis.json").exists()


def test_total_entries(report):
    """total_entries must equal 100."""
    assert report["total_entries"] == 100


def test_severity_counts_sum(report):
    """Sum of all severity counts must equal total entries."""
    counts = report["severity_counts"]
    total = sum(counts.values())
    assert total == report["total_entries"], f"Severity counts sum {total} != total {report['total_entries']}"


def test_severity_info_count(report):
    """INFO count should be the most common (around 55-60)."""
    assert report["severity_counts"]["INFO"] > 50
    assert report["severity_counts"]["INFO"] < 65


def test_severity_error_count(report):
    """ERROR count should be around 18-22."""
    assert report["severity_counts"]["ERROR"] > 15
    assert report["severity_counts"]["ERROR"] < 25


def test_severity_critical_count(report):
    """CRITICAL count should be exactly 5."""
    assert report["severity_counts"]["CRITICAL"] == 5


def test_severity_warning_count(report):
    """WARNING count should be around 16-20."""
    assert report["severity_counts"]["WARNING"] > 13
    assert report["severity_counts"]["WARNING"] < 23


def test_top_error_sources_present(report):
    """top_error_sources must be a non-empty list."""
    assert len(report["top_error_sources"]) > 0
    assert len(report["top_error_sources"]) <= 5


def test_top_error_source_is_sshd_or_mysql(report):
    """sshd and mysql should be among the top error sources."""
    sources = {e["source"] for e in report["top_error_sources"]}
    assert "sshd" in sources, "sshd should be a top error source"
    assert "mysql" in sources or "docker" in sources, "mysql or docker should be a top error source"


def test_top_error_sources_sorted(report):
    """top_error_sources must be sorted by error_count descending."""
    counts = [e["error_count"] for e in report["top_error_sources"]]
    for i in range(len(counts) - 1):
        assert counts[i] >= counts[i + 1], "top_error_sources not sorted descending"


def test_peak_hour(report):
    """Peak hour should be one of the busiest hours (8, 9, 10, or 11)."""
    assert report["peak_hour"] in [8, 9, 10, 11], f"Unexpected peak hour: {report['peak_hour']}"


def test_entries_per_hour_present(report):
    """entries_per_hour must have entries for multiple hours."""
    assert len(report["entries_per_hour"]) >= 10


def test_critical_entries_count(report):
    """critical_entries must list all CRITICAL entries (5 total)."""
    assert len(report["critical_entries"]) == 5


def test_critical_entries_have_fields(report):
    """Each critical entry must have timestamp, source, and message."""
    for entry in report["critical_entries"]:
        assert "timestamp" in entry
        assert "source" in entry
        assert "message" in entry


def test_critical_sources(report):
    """Critical entries should come from mysql, docker, and disk_monitor."""
    sources = {e["source"] for e in report["critical_entries"]}
    assert "mysql" in sources
    assert "docker" in sources
    assert "disk_monitor" in sources
