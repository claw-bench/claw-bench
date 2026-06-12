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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "cron_explained.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            assert v is not None, f"Item {i}: field '{k}' is null"
            if isinstance(v, str):
                assert v.strip() != "", f"Item {i}: field '{k}' is empty string"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "cron_explained.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "cron_explained.json"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"
