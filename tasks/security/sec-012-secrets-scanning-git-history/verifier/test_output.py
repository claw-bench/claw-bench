"""Verifier for sec-012: Secrets Scanning in Git History."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the secrets report JSON."""
    path = workspace / "secrets_report.json"
    assert path.exists(), "secrets_report.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "secrets_report.json must contain a JSON array"
    return data


def _find_by_commit(report, commit_id):
    """Find entries for a given commit."""
    return [r for r in report if r.get("commit") == commit_id]


COMMITS_WITH_SECRETS = ["commit_01", "commit_03", "commit_05", "commit_07", "commit_09"]
CLEAN_COMMITS = ["commit_02", "commit_04", "commit_06", "commit_08", "commit_10"]


def test_report_file_exists(workspace):
    """secrets_report.json must exist."""
    assert (workspace / "secrets_report.json").exists()


def test_minimum_secrets_found(report):
    """Must detect at least 6 secrets."""
    assert len(report) >= 6, f"Expected at least 6 secrets, got {len(report)}"


def test_aws_keys_found(report):
    """AWS credentials in commit_01 must be detected."""
    matches = _find_by_commit(report, "commit_01")
    assert len(matches) >= 1, "AWS credentials in commit_01 not detected"
    types = {m.get("secret_type", "").lower() for m in matches}
    assert any("aws" in t or "key" in t for t in types), (
        f"AWS key type not identified, got: {types}"
    )


def test_database_credential_found(report):
    """Database credential in commit_03 must be detected."""
    matches = _find_by_commit(report, "commit_03")
    assert len(matches) >= 1, "Database credential in commit_03 not detected"


def test_stripe_key_found(report):
    """Stripe API key in commit_05 must be detected."""
    matches = _find_by_commit(report, "commit_05")
    assert len(matches) >= 1, "Stripe/GitHub keys in commit_05 not detected"


def test_private_key_found(report):
    """RSA private key in commit_07 must be detected."""
    matches = _find_by_commit(report, "commit_07")
    assert len(matches) >= 1, "Private key in commit_07 not detected"
    types = {m.get("secret_type", "").lower() for m in matches}
    assert any("private" in t or "key" in t or "pem" in t or "rsa" in t for t in types)


def test_jwt_secret_found(report):
    """JWT secret in commit_09 must be detected."""
    matches = _find_by_commit(report, "commit_09")
    assert len(matches) >= 1, "JWT secret in commit_09 not detected"


def test_clean_commits_not_flagged(report):
    """Clean commits should not be flagged."""
    for commit in CLEAN_COMMITS:
        matches = _find_by_commit(report, commit)
        assert len(matches) == 0, f"Clean commit {commit} incorrectly flagged"


def test_each_entry_has_required_fields(report):
    """Each entry must have commit, file, secret_type, remediation."""
    for entry in report:
        assert "commit" in entry, "Missing 'commit' field"
        assert "file" in entry, "Missing 'file' field"
        assert "secret_type" in entry, "Missing 'secret_type' field"
        assert "remediation" in entry, "Missing 'remediation' field"


def test_remediation_not_empty(report):
    """Each entry must have a non-empty remediation recommendation."""
    for entry in report:
        assert len(entry.get("remediation", "")) > 10, (
            f"Remediation too short for {entry.get('commit')}/{entry.get('file')}"
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
    path = workspace / "secrets_report.json"
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
    path = workspace / "secrets_report.json"
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
    path = workspace / "secrets_report.json"
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
