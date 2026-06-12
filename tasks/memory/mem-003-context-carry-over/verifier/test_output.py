"""Verifier for mem-003: Context Carry-Over."""

import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


def test_db_connection_exists(workspace):
    """db_connection.txt must exist."""
    assert (workspace / "db_connection.txt").exists(), "db_connection.txt not found"


def test_db_connection_string(workspace):
    """db_connection.txt must contain the correct PostgreSQL connection string."""
    content = (workspace / "db_connection.txt").read_text().strip()
    assert content == "postgresql://app_service:xK9#mP2$vL5n@db.internal.example.com:5432/inventory_prod", (
        f"Incorrect connection string: {content}"
    )


def test_feature_report_exists(workspace):
    """feature_report.txt must exist."""
    assert (workspace / "feature_report.txt").exists(), "feature_report.txt not found"


def test_feature_report_content(workspace):
    """feature_report.txt must list all features with correct ENABLED/DISABLED status."""
    content = (workspace / "feature_report.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    assert len(lines) == 5, f"Expected 5 feature lines, got {len(lines)}"

    expected = {
        "dark_mode": "ENABLED",
        "beta_dashboard": "DISABLED",
        "export_csv": "ENABLED",
        "multi_language": "DISABLED",
        "audit_logging": "ENABLED",
    }

    for line in lines:
        parts = line.split(":")
        name = parts[0].strip()
        status = parts[1].strip()
        assert name in expected, f"Unexpected feature: {name}"
        assert status == expected[name], (
            f"Feature '{name}' should be {expected[name]}, got {status}"
        )


def test_feature_report_order(workspace):
    """Features must appear in the same order as in config.json."""
    content = (workspace / "feature_report.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    names = [line.split(":")[0].strip() for line in lines]
    expected_order = ["dark_mode", "beta_dashboard", "export_csv", "multi_language", "audit_logging"]
    assert names == expected_order, f"Features not in expected order: {names}"


def test_notification_summary_exists(workspace):
    """notification_summary.txt must exist."""
    assert (workspace / "notification_summary.txt").exists(), (
        "notification_summary.txt not found"
    )


def test_notification_email(workspace):
    """Notification summary must show email as on with correct recipient."""
    content = (workspace / "notification_summary.txt").read_text()
    assert "Email notifications: on" in content, "Email should be on"
    assert "ops-team@example.com" in content, "Email recipient missing"


def test_notification_sms(workspace):
    """Notification summary must show SMS as off with correct phone."""
    content = (workspace / "notification_summary.txt").read_text()
    assert "SMS notifications: off" in content, "SMS should be off"
    assert "+1-555-0142" in content, "SMS phone missing"


def test_notification_slack(workspace):
    """Slack webhook should be 'not configured' since no URL is provided."""
    content = (workspace / "notification_summary.txt").read_text()
    assert "not configured" in content.lower(), (
        "Slack webhook should show 'not configured'"
    )


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
    path = workspace / "config.json"
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
    path = workspace / "config.json"
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
    path = workspace / "config.json"
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
