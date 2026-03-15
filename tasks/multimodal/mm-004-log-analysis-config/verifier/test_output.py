"""Verifier for mm-004: Log Analysis with Config."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report_text(workspace):
    path = workspace / "report.txt"
    assert path.exists(), "report.txt not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    assert (workspace / "report.txt").exists()


def test_total_log_entries(report_text):
    assert "Total log entries: 21" in report_text


def test_error_count(report_text):
    assert "Error count: 13" in report_text


def test_warning_count(report_text):
    assert "Warning count: 4" in report_text


def test_threshold_violations_section(report_text):
    assert "Threshold Violations:" in report_text


def test_auth_threshold_violation(report_text):
    assert "auth: 5 errors (threshold: 3)" in report_text


def test_payments_threshold_violation(report_text):
    assert "payments: 4 errors (threshold: 2)" in report_text


def test_gateway_no_violation(report_text):
    """Gateway has 0 errors, should not be a violation."""
    lines = report_text.split("\n")
    violation_lines = [l for l in lines if l.startswith("- gateway:") and "errors" in l]
    assert len(violation_lines) == 0


def test_unknown_services_section(report_text):
    assert "Unknown Services:" in report_text


def test_analytics_unknown(report_text):
    """analytics is not in config.yaml, should be listed as unknown."""
    assert "- analytics" in report_text


def test_port_mismatches_section(report_text):
    assert "Port Mismatches:" in report_text


def test_payments_port_mismatch(report_text):
    assert "payments: log port 9090, config port 9091" in report_text


def test_auth_no_port_mismatch(report_text):
    """auth uses port 8080 in both log and config, no mismatch."""
    lines = report_text.split("\n")
    mismatch_lines = [l for l in lines if l.startswith("- auth:") and "log port" in l]
    assert len(mismatch_lines) == 0


def test_sections_in_order(report_text):
    """Sections must appear in the specified order."""
    pos_total = report_text.index("Total log entries:")
    pos_violations = report_text.index("Threshold Violations:")
    pos_unknown = report_text.index("Unknown Services:")
    pos_port = report_text.index("Port Mismatches:")
    assert pos_total < pos_violations < pos_unknown < pos_port
