"""Verifier for sec-007: Log Forensics."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def incidents(workspace):
    """Load and return the security incidents JSON."""
    path = workspace / "security_incidents.json"
    assert path.exists(), "security_incidents.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "security_incidents.json must contain a JSON array"
    return data


def _find_incident(incidents, incident_type):
    """Find an incident by type."""
    return [i for i in incidents if i.get("type") == incident_type]


def test_incidents_file_exists(workspace):
    """security_incidents.json must exist."""
    assert (workspace / "security_incidents.json").exists()


def test_three_incidents_detected(incidents):
    """Must detect exactly 3 incident patterns."""
    assert len(incidents) >= 3, f"Expected at least 3 incidents, got {len(incidents)}"


def test_brute_force_detected(incidents):
    """Brute force attack from 10.0.0.55 must be detected."""
    bf = _find_incident(incidents, "brute_force")
    assert len(bf) >= 1, "Brute force attack not detected"
    assert bf[0]["source_ip"] == "10.0.0.55", (
        f"Wrong brute force IP: {bf[0]['source_ip']}"
    )


def test_scanning_detected(incidents):
    """Scanning activity from 172.16.0.99 must be detected."""
    scans = _find_incident(incidents, "scanning")
    assert len(scans) >= 1, "Scanning activity not detected"
    assert scans[0]["source_ip"] == "172.16.0.99", (
        f"Wrong scanning IP: {scans[0]['source_ip']}"
    )


def test_off_hours_access_detected(incidents):
    """Off-hours admin access from 10.0.0.200 must be detected."""
    oha = _find_incident(incidents, "off_hours_access")
    assert len(oha) >= 1, "Off-hours access not detected"
    assert oha[0]["source_ip"] == "10.0.0.200", (
        f"Wrong off-hours IP: {oha[0]['source_ip']}"
    )


def test_each_incident_has_required_fields(incidents):
    """Each incident must have type, source_ip, description, severity."""
    for inc in incidents:
        assert "type" in inc, "Missing 'type' field"
        assert "source_ip" in inc, "Missing 'source_ip' field"
        assert "description" in inc, "Missing 'description' field"
        assert "severity" in inc, "Missing 'severity' field"


def test_severity_values(incidents):
    """Severity must be high, medium, or low."""
    for inc in incidents:
        assert inc["severity"] in ("high", "medium", "low"), (
            f"Invalid severity: {inc['severity']}"
        )


def test_brute_force_has_evidence(incidents):
    """Brute force incident must include evidence (log line refs)."""
    bf = _find_incident(incidents, "brute_force")
    assert len(bf) >= 1
    assert "evidence" in bf[0], "Brute force incident missing evidence"
    assert len(bf[0]["evidence"]) >= 5, "Brute force evidence should reference multiple log lines"


def test_incident_descriptions_not_empty(incidents):
    """Each incident must have a non-empty description."""
    for inc in incidents:
        assert len(inc.get("description", "")) > 10, (
            f"Description too short for {inc.get('type', 'unknown')}"
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
    path = workspace / "security_incidents.json"
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
    path = workspace / "security_incidents.json"
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
    path = workspace / "security_incidents.json"
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
