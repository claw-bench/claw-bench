"""Verifier for sys-005: Cron Expression Parser."""

import json
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the cron_explained.json contents."""
    path = workspace / "cron_explained.json"
    assert path.exists(), "cron_explained.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """cron_explained.json must exist in the workspace."""
    assert (workspace / "cron_explained.json").exists()


def test_total_entries(report):
    """total_entries must equal 8."""
    assert report["total_entries"] == 8


def test_all_entries_parsed(report):
    """entries array must have exactly 8 items."""
    assert len(report["entries"]) == 8


def test_entries_have_required_fields(report):
    """Each entry must have expression, command, description, and next_runs."""
    for entry in report["entries"]:
        assert "expression" in entry, "Missing 'expression'"
        assert "command" in entry, "Missing 'command'"
        assert "description" in entry, "Missing 'description'"
        assert "next_runs" in entry, "Missing 'next_runs'"


def test_each_entry_has_three_next_runs(report):
    """Each entry must have exactly 3 next run times."""
    for entry in report["entries"]:
        assert len(entry["next_runs"]) == 3, (
            f"Entry '{entry['expression']}' has {len(entry['next_runs'])} next_runs, expected 3"
        )


def test_next_runs_are_valid_datetimes(report):
    """All next_runs must be valid ISO 8601 datetimes."""
    for entry in report["entries"]:
        for run in entry["next_runs"]:
            try:
                datetime.fromisoformat(run)
            except ValueError:
                pytest.fail(f"Invalid datetime: {run}")


def test_next_runs_are_chronological(report):
    """next_runs within each entry must be in chronological order."""
    for entry in report["entries"]:
        times = [datetime.fromisoformat(r) for r in entry["next_runs"]]
        for i in range(len(times) - 1):
            assert times[i] < times[i + 1], (
                f"next_runs not chronological for '{entry['expression']}': {entry['next_runs']}"
            )


def test_every_15_minutes_description(report):
    """The */15 * * * * entry must describe running every 15 minutes."""
    entry = [e for e in report["entries"] if "*/15" in e["expression"]]
    assert len(entry) == 1
    desc = entry[0]["description"].lower()
    assert "15" in desc and "minute" in desc, f"Description not clear: {entry[0]['description']}"


def test_daily_backup_description(report):
    """The 0 2 * * * entry must describe daily at 2 AM."""
    entry = [e for e in report["entries"] if e["expression"].startswith("0 2 * * *")]
    assert len(entry) == 1
    desc = entry[0]["description"].lower()
    assert ("2" in desc and ("am" in desc or "02:00" in desc or "day" in desc or "daily" in desc)), \
        f"Description not clear for daily backup: {entry[0]['description']}"


def test_monthly_cleanup_description(report):
    """The 0 0 1 * * entry must describe monthly on the 1st."""
    entry = [e for e in report["entries"] if e["expression"].startswith("0 0 1 * *")]
    assert len(entry) == 1
    desc = entry[0]["description"].lower()
    assert "month" in desc or "1st" in desc or "first" in desc, \
        f"Description not clear for monthly: {entry[0]['description']}"


def test_weekly_sunday_description(report):
    """The 0 3 * * 0 entry must describe weekly on Sunday."""
    entry = [e for e in report["entries"] if e["expression"].startswith("0 3 * * 0")]
    assert len(entry) == 1
    desc = entry[0]["description"].lower()
    assert "sunday" in desc or "week" in desc, \
        f"Description not clear for weekly: {entry[0]['description']}"


def test_commands_preserved(report):
    """Commands must be preserved correctly."""
    commands = {e["command"] for e in report["entries"]}
    assert "/usr/local/bin/health_check.sh" in commands
    assert "/usr/local/bin/backup.sh --full" in commands
    assert "/opt/scripts/report_gen.py" in commands
