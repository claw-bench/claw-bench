"""Verifier for sys-009: Performance Diagnostic."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the diagnosis.json contents."""
    path = workspace / "diagnosis.json"
    assert path.exists(), "diagnosis.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """diagnosis.json must exist in the workspace."""
    assert (workspace / "diagnosis.json").exists()


def test_analysis_period(report):
    """Analysis period must cover 24 data points."""
    assert report["analysis_period"]["data_points"] == 24


def test_cpu_stats_present(report):
    """CPU stats must include mean, max, and min."""
    cpu = report["cpu"]
    assert "mean" in cpu
    assert "max" in cpu
    assert "min" in cpu


def test_cpu_max_value(report):
    """CPU max should be 95.8%."""
    assert report["cpu"]["max"] == pytest.approx(95.8, abs=0.5)


def test_cpu_min_value(report):
    """CPU min should be 10.2%."""
    assert report["cpu"]["min"] == pytest.approx(10.2, abs=0.5)


def test_memory_stats_present(report):
    """Memory stats must include mean, max, and min."""
    mem = report["memory"]
    assert "mean" in mem
    assert "max" in mem
    assert "min" in mem


def test_memory_max_value(report):
    """Memory max should be 91.7%."""
    assert report["memory"]["max"] == pytest.approx(91.7, abs=0.5)


def test_disk_io_stats_present(report):
    """Disk I/O stats must include mean, max, and min."""
    dio = report["disk_io"]
    assert "mean" in dio
    assert "max" in dio
    assert "min" in dio


def test_disk_io_max_is_spike(report):
    """Disk I/O max should be 145.2 MB/s (the hour 12 spike)."""
    assert report["disk_io"]["max"] == pytest.approx(145.2, abs=1.0)


def test_cpu_bottleneck_detected(report):
    """A CPU bottleneck should be detected during peak hours."""
    cpu_bottlenecks = [b for b in report["bottlenecks"] if b["resource"] == "cpu"]
    assert len(cpu_bottlenecks) > 0, "No CPU bottleneck detected"
    # Peak CPU is at hours 14-16 (>90%)
    bn = cpu_bottlenecks[0]
    assert bn["time_window"]["start_hour"] <= 15
    assert bn["time_window"]["end_hour"] >= 15


def test_memory_bottleneck_detected(report):
    """A memory bottleneck should be detected."""
    mem_bottlenecks = [b for b in report["bottlenecks"] if b["resource"] == "memory"]
    assert len(mem_bottlenecks) > 0, "No memory bottleneck detected"


def test_disk_io_anomaly_or_bottleneck(report):
    """Disk I/O spike at hour 12 (145.2 MB/s) should be detected as anomaly or bottleneck."""
    dio_anomalies = report["disk_io"].get("anomalies", [])
    dio_bottlenecks = [b for b in report["bottlenecks"] if b["resource"] == "disk_io"]
    hour_12_anomaly = any(a["hour"] == 12 for a in dio_anomalies)
    has_dio_bottleneck = len(dio_bottlenecks) > 0
    assert hour_12_anomaly or has_dio_bottleneck, (
        "Disk I/O spike at hour 12 not detected as anomaly or bottleneck"
    )


def test_bottleneck_time_windows(report):
    """Each bottleneck must have a valid time_window with start and end hours."""
    for bn in report["bottlenecks"]:
        assert "time_window" in bn
        tw = bn["time_window"]
        assert "start_hour" in tw
        assert "end_hour" in tw
        assert 0 <= tw["start_hour"] <= 23
        assert 0 <= tw["end_hour"] <= 23
        assert tw["start_hour"] <= tw["end_hour"]


def test_recommendations_present(report):
    """At least 3 actionable recommendations must be provided."""
    assert len(report["recommendations"]) >= 3
    for rec in report["recommendations"]:
        assert len(rec) > 20, f"Recommendation too short: {rec}"


def test_bottleneck_severity(report):
    """Bottleneck severity must be 'warning' or 'critical'."""
    for bn in report["bottlenecks"]:
        assert bn["severity"] in ("warning", "critical"), (
            f"Invalid severity: {bn['severity']}"
        )


def test_cpu_critical_severity(report):
    """CPU bottleneck should be critical (peak > 90%)."""
    cpu_bottlenecks = [b for b in report["bottlenecks"] if b["resource"] == "cpu"]
    if cpu_bottlenecks:
        assert cpu_bottlenecks[0]["severity"] == "critical", (
            "CPU bottleneck should be critical (peaks at 95.8%)"
        )
