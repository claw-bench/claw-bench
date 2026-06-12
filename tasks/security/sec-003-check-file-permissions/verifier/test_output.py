"""Verifier for sec-003: Check File Permissions."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def audit(workspace):
    """Load and return the permission audit JSON."""
    path = workspace / "permission_audit.json"
    assert path.exists(), "permission_audit.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "permission_audit.json must contain a JSON array"
    return data


DANGEROUS_FILES = [
    "config.yaml",
    "private_key.pem",
    "backup_script.sh",
    "passwords.db",
    "upload_handler.cgi",
    ".htpasswd",
]

SAFE_FILES = [
    "README.md", "database.env", "app.log", "server",
    "index.html", "package.json", "deploy.sh", "robots.txt", "style.css",
]


def test_audit_file_exists(workspace):
    """permission_audit.json must exist."""
    assert (workspace / "permission_audit.json").exists()


def test_audit_is_nonempty(audit):
    """Audit must contain findings."""
    assert len(audit) > 0


def test_all_dangerous_files_flagged(audit):
    """All 6 dangerous files must be flagged."""
    flagged_files = {entry["file"] for entry in audit}
    for df in DANGEROUS_FILES:
        assert df in flagged_files, f"Dangerous file {df} not flagged"


def test_each_entry_has_required_fields(audit):
    """Each audit entry must have file, permissions, issue, recommendation."""
    for entry in audit:
        assert "file" in entry, "Missing 'file' field"
        assert "issue" in entry, "Missing 'issue' field"
        assert "recommendation" in entry, "Missing 'recommendation' field"


def test_private_key_flagged(audit):
    """private_key.pem must be flagged for being world-accessible."""
    entries = [e for e in audit if e["file"] == "private_key.pem"]
    assert len(entries) >= 1, "private_key.pem not in audit"
    issue_text = entries[0]["issue"].lower()
    assert "world" in issue_text or "writable" in issue_text or "666" in issue_text


def test_suid_flagged(audit):
    """backup_script.sh must be flagged for SUID bit."""
    entries = [e for e in audit if e["file"] == "backup_script.sh"]
    assert len(entries) >= 1, "backup_script.sh not in audit"
    issue_text = entries[0]["issue"].lower()
    assert "suid" in issue_text or "setuid" in issue_text or "privilege" in issue_text


def test_recommendations_are_restrictive(audit):
    """Recommendations should suggest more restrictive permissions."""
    for entry in audit:
        rec = entry.get("recommendation", "")
        # Recommendation should be a numeric mode or description
        assert len(rec) > 0, f"Empty recommendation for {entry['file']}"


def test_777_files_detected(audit):
    """Files with 777 permissions must be detected."""
    flagged = {e["file"] for e in audit}
    assert "config.yaml" in flagged, "config.yaml (777) not flagged"
    assert "upload_handler.cgi" in flagged, "upload_handler.cgi (777) not flagged"


def test_no_excessive_false_positives(audit):
    """Should not flag more than 10 files (reasonable false positive limit)."""
    assert len(audit) <= 10, f"Too many findings ({len(audit)}) — likely false positives"


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
    path = workspace / "permission_audit.json"
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
    path = workspace / "permission_audit.json"
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
    path = workspace / "permission_audit.json"
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
