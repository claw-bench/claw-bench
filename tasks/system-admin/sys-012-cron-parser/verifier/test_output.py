"""Verifier for sys-012: Cron Parser."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    path = Path(workspace) / "cron_schedule.json"
    assert path.exists(), "cron_schedule.json not found in workspace"
    return json.loads(path.read_text())


def test_report_file_exists(workspace):
    assert (Path(workspace) / "cron_schedule.json").exists()


def test_total_jobs(report):
    assert report["total_jobs"] == 8


def test_jobs_count(report):
    assert len(report["jobs"]) == 8


def test_jobs_have_required_fields(report):
    for job in report["jobs"]:
        assert "command" in job
        assert "schedule_human" in job
        assert "cron_expression" in job


def test_backup_db_job(report):
    job = next((j for j in report["jobs"] if "backup-db" in j["command"]), None)
    assert job is not None, "backup-db job not found"
    assert job["cron_expression"] == "30 2 * * *"
    human = job["schedule_human"].lower()
    assert "daily" in human or "02:30" in job["schedule_human"]


def test_logrotate_job(report):
    job = next((j for j in report["jobs"] if "logrotate" in j["command"]), None)
    assert job is not None, "logrotate job not found"
    assert job["cron_expression"] == "0 * * * *"
    human = job["schedule_human"].lower()
    assert "hour" in human


def test_security_scan_job(report):
    job = next((j for j in report["jobs"] if "scan.sh" in j["command"]), None)
    assert job is not None, "security scan job not found"
    assert job["cron_expression"] == "0 0 * * 0"
    human = job["schedule_human"].lower()
    assert "sunday" in human or "weekly" in human


def test_disk_check_job(report):
    job = next((j for j in report["jobs"] if "check-disk" in j["command"]), None)
    assert job is not None, "check-disk job not found"
    assert job["cron_expression"] == "*/15 * * * *"
    human = job["schedule_human"].lower()
    assert "15" in human and "minute" in human


def test_monthly_report_job(report):
    job = next((j for j in report["jobs"] if "monthly-report" in j["command"]), None)
    assert job is not None, "monthly-report job not found"
    assert job["cron_expression"] == "0 0 1 * *"
    human = job["schedule_human"].lower()
    assert "monthly" in human


def test_sync_files_job(report):
    job = next((j for j in report["jobs"] if "sync-files" in j["command"]), None)
    assert job is not None, "sync-files job not found"
    assert job["cron_expression"] == "0 3 * * 1-5"
    human = job["schedule_human"].lower()
    assert "weekday" in human


def test_license_check_job(report):
    job = next((j for j in report["jobs"] if "license-check" in j["command"]), None)
    assert job is not None, "license-check job not found"
    assert job["cron_expression"] == "0 0 1 1 *"
    human = job["schedule_human"].lower()
    assert "year" in human or "january" in human


def test_service_monitor_job(report):
    job = next((j for j in report["jobs"] if "service-monitor" in j["command"]), None)
    assert job is not None, "service-monitor job not found"
    assert job["cron_expression"] == "0 6,18 * * *"
    human = job["schedule_human"].lower()
    assert "06:00" in job["schedule_human"] and "18:00" in job["schedule_human"]


def test_comments_excluded(report):
    """No job should have a command starting with #."""
    for job in report["jobs"]:
        assert not job["command"].startswith("#")


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "cron_schedule.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

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
    path = workspace / "cron_schedule.json"
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
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "cron_schedule.json"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
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
