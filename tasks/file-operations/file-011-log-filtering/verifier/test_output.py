"""Verifier for file-011: Log File Filtering."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def errors_text(workspace):
    """Read and return the generated errors.txt contents."""
    path = workspace / "errors.txt"
    assert path.exists(), "errors.txt not found in workspace"
    return path.read_text().strip()


def test_output_file_exists(workspace):
    """errors.txt must exist in the workspace."""
    assert (workspace / "errors.txt").exists()


def test_only_error_and_warn_lines(errors_text):
    """Every line must contain [ERROR] or [WARN]."""
    lines = errors_text.splitlines()
    for line in lines:
        assert "[ERROR]" in line or "[WARN]" in line, (
            f"Line should contain [ERROR] or [WARN]: {line}"
        )


def test_no_info_or_debug_lines(errors_text):
    """No lines should contain [INFO] or [DEBUG]."""
    lines = errors_text.splitlines()
    for line in lines:
        assert "[INFO]" not in line, f"Line should not contain [INFO]: {line}"
        assert "[DEBUG]" not in line, f"Line should not contain [DEBUG]: {line}"


def test_correct_total_count(errors_text):
    """There should be exactly 15 filtered lines (6 ERROR + 9 WARN)."""
    lines = [l for l in errors_text.splitlines() if l.strip()]
    assert len(lines) == 15, f"Expected 15 filtered lines, got {len(lines)}"


def test_correct_error_count(errors_text):
    """There should be exactly 6 ERROR lines."""
    error_lines = [l for l in errors_text.splitlines() if "[ERROR]" in l]
    assert len(error_lines) == 6, f"Expected 6 ERROR lines, got {len(error_lines)}"


def test_correct_warn_count(errors_text):
    """There should be exactly 9 WARN lines."""
    warn_lines = [l for l in errors_text.splitlines() if "[WARN]" in l]
    assert len(warn_lines) == 9, f"Expected 9 WARN lines, got {len(warn_lines)}"


def test_timestamps_preserved(errors_text):
    """Each line should have a valid timestamp."""
    import re
    lines = errors_text.splitlines()
    ts_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
    for line in lines:
        assert ts_pattern.match(line), f"Line missing timestamp: {line}"


def test_correct_order(errors_text):
    """Lines should be in chronological order."""
    lines = errors_text.splitlines()
    timestamps = []
    for line in lines:
        ts = line[:19]  # "YYYY-MM-DD HH:MM:SS"
        timestamps.append(ts)
    for i in range(len(timestamps) - 1):
        assert timestamps[i] <= timestamps[i + 1], (
            f"Lines out of order: '{timestamps[i]}' > '{timestamps[i+1]}'"
        )
