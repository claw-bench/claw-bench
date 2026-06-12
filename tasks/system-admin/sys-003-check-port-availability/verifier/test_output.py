"""Verifier for sys-003: Check Port Availability."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the port_report.json contents."""
    path = workspace / "port_report.json"
    assert path.exists(), "port_report.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """port_report.json must exist in the workspace."""
    assert (workspace / "port_report.json").exists()


def test_total_listening_ports(report):
    """total_listening_ports must equal 12."""
    assert report["total_listening_ports"] == 12


def test_ports_sorted_ascending(report):
    """Ports array must be sorted by port number ascending."""
    port_numbers = [p["port"] for p in report["ports"]]
    assert port_numbers == sorted(port_numbers), "Ports not sorted ascending"


def test_well_known_ports(report):
    """well_known_ports must include ports 22, 25, 53, 80, 443."""
    expected = {22, 25, 53, 80, 443}
    found = set(report["well_known_ports"])
    assert expected.issubset(found), f"Missing well-known ports: {expected - found}"


def test_high_ports(report):
    """high_ports must include ports 3000, 3306, 5432, 6379, 8080, 9090, 9100."""
    expected = {3000, 3306, 5432, 6379, 8080, 9090, 9100}
    found = set(report["high_ports"])
    assert expected.issubset(found), f"Missing high ports: {expected - found}"


def test_ssh_service_identified(report):
    """Port 22 must be identified as ssh service."""
    port_22 = [p for p in report["ports"] if p["port"] == 22]
    assert len(port_22) == 1
    assert port_22[0]["service"] == "ssh"


def test_mysql_service_identified(report):
    """Port 3306 must be identified as mysql service."""
    port_3306 = [p for p in report["ports"] if p["port"] == 3306]
    assert len(port_3306) == 1
    assert port_3306[0]["service"] == "mysql"


def test_http_service_identified(report):
    """Port 80 must be identified as http service."""
    port_80 = [p for p in report["ports"] if p["port"] == 80]
    assert len(port_80) == 1
    assert port_80[0]["service"] == "http"


def test_entries_have_required_fields(report):
    """Each port entry must have all required fields."""
    required = {"port", "bind_address", "protocol", "process_name", "service"}
    for entry in report["ports"]:
        for field in required:
            assert field in entry, f"Entry missing '{field}' field"


def test_bind_address_present(report):
    """Bind addresses must be present and valid."""
    for entry in report["ports"]:
        addr = entry["bind_address"]
        assert addr in ["0.0.0.0", "127.0.0.1", "::", "::1"], f"Unexpected bind address: {addr}"


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
    path = workspace / "port_report.json"
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
    path = workspace / "port_report.json"
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
    path = workspace / "port_report.json"
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
