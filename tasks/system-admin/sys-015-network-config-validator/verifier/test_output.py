"""Verifier for sys-015: Network Config Validator."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def report(workspace):
    path = Path(workspace) / "validation_report.json"
    assert path.exists(), "validation_report.json not found in workspace"
    return json.loads(path.read_text())


def _get_iface(report, name):
    for iface in report["interfaces"]:
        if iface["name"] == name:
            return iface
    return None


def test_report_file_exists(workspace):
    assert (Path(workspace) / "validation_report.json").exists()


def test_total_interfaces(report):
    assert report["summary"]["total_interfaces"] == 6


def test_valid_count(report):
    assert report["summary"]["valid_count"] == 3


def test_invalid_count(report):
    assert report["summary"]["invalid_count"] == 3


def test_all_interfaces_present(report):
    names = {iface["name"] for iface in report["interfaces"]}
    expected = {"eth0", "eth1", "eth2", "eth3", "eth4", "eth5"}
    assert names == expected


def test_interfaces_have_required_fields(report):
    for iface in report["interfaces"]:
        assert "name" in iface
        assert "ip" in iface
        assert "subnet_mask" in iface
        assert "gateway" in iface
        assert "dns" in iface
        assert "valid" in iface
        assert "errors" in iface


def test_eth0_valid(report):
    iface = _get_iface(report, "eth0")
    assert iface["valid"] is True
    assert iface["errors"] == []


def test_eth1_valid(report):
    iface = _get_iface(report, "eth1")
    assert iface["valid"] is True
    assert iface["errors"] == []


def test_eth2_valid(report):
    iface = _get_iface(report, "eth2")
    assert iface["valid"] is True
    assert iface["errors"] == []


def test_eth3_invalid_ip(report):
    """eth3 has IP 999.168.1.10 which is invalid."""
    iface = _get_iface(report, "eth3")
    assert iface["valid"] is False
    error_text = " ".join(iface["errors"]).lower()
    assert "invalid_ip" in error_text


def test_eth4_gateway_not_in_subnet(report):
    """eth4 has IP 192.168.2.100/24 but gateway 192.168.3.1 (different subnet)."""
    iface = _get_iface(report, "eth4")
    assert iface["valid"] is False
    error_text = " ".join(iface["errors"]).lower()
    assert "gateway_not_in_subnet" in error_text


def test_eth4_invalid_dns(report):
    """eth4 has DNS 300.1.1.1 which is invalid."""
    iface = _get_iface(report, "eth4")
    error_text = " ".join(iface["errors"]).lower()
    assert "invalid_dns" in error_text


def test_eth5_network_address(report):
    """eth5 has IP 10.10.10.0 with /24 mask - that is the network address."""
    iface = _get_iface(report, "eth5")
    assert iface["valid"] is False
    error_text = " ".join(iface["errors"]).lower()
    assert "ip_is_network_address" in error_text


def test_valid_interfaces_have_no_errors(report):
    for iface in report["interfaces"]:
        if iface["valid"]:
            assert iface["errors"] == [], f"{iface['name']} marked valid but has errors"


def test_invalid_interfaces_have_errors(report):
    for iface in report["interfaces"]:
        if not iface["valid"]:
            assert len(iface["errors"]) > 0, f"{iface['name']} marked invalid but has no errors"


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
    path = workspace / "network_config.json"
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
    path = workspace / "network_config.json"
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
    path = workspace / "network_config.json"
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
