"""Verifier for sec-013: Threat Model Generation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def threat_model(workspace):
    """Load and return the threat model JSON."""
    path = workspace / "threat_model.json"
    assert path.exists(), "threat_model.json not found in workspace"
    data = json.loads(path.read_text())
    return data


@pytest.fixture
def threat_report(workspace):
    """Load and return the threat report markdown."""
    path = workspace / "threat_report.md"
    assert path.exists(), "threat_report.md not found in workspace"
    return path.read_text()


STRIDE_CATEGORIES = ["Spoofing", "Tampering", "Repudiation",
                     "Information Disclosure", "Denial of Service",
                     "Elevation of Privilege"]

ALL_COMPONENTS = ["api-gateway", "user-service", "order-service",
                  "payment-service", "notification-service", "admin-dashboard"]


def test_threat_model_exists(workspace):
    """threat_model.json must exist."""
    assert (workspace / "threat_model.json").exists()


def test_threat_report_exists(workspace):
    """threat_report.md must exist."""
    assert (workspace / "threat_report.md").exists()


def test_has_metadata(threat_model):
    """Threat model must include metadata."""
    assert "metadata" in threat_model
    meta = threat_model["metadata"]
    assert "methodology" in meta or "system_name" in meta


def test_has_threats(threat_model):
    """Threat model must include a threats array."""
    assert "threats" in threat_model
    assert isinstance(threat_model["threats"], list)
    assert len(threat_model["threats"]) >= 6, "Expected at least 6 threats"


def test_all_stride_categories_covered(threat_model):
    """All 6 STRIDE categories must be represented."""
    categories = {t.get("category", "").lower() for t in threat_model["threats"]}
    # Normalize: check first letter or common abbreviations
    stride_found = set()
    for cat in categories:
        for stride in STRIDE_CATEGORIES:
            if stride.lower() in cat or cat.startswith(stride[0].lower()):
                stride_found.add(stride)
    # Also check single-letter abbreviations
    for t in threat_model["threats"]:
        c = t.get("category", "")
        if c in ("S", "T", "R", "I", "D", "E"):
            stride_found.add(STRIDE_CATEGORIES["STRIDE".index(c)])
    missing = set(STRIDE_CATEGORIES) - stride_found
    assert len(missing) == 0, f"Missing STRIDE categories: {missing}"


def test_multiple_components_analyzed(threat_model):
    """Threats must cover at least 4 different components."""
    components = {t.get("component", "") for t in threat_model["threats"]}
    assert len(components) >= 4, (
        f"Only {len(components)} components analyzed, expected at least 4"
    )


def test_each_threat_has_required_fields(threat_model):
    """Each threat must have category, component, description, mitigation."""
    for t in threat_model["threats"]:
        assert "category" in t, "Missing 'category' field"
        assert "component" in t, "Missing 'component' field"
        assert "description" in t, "Missing 'description' field"
        assert "mitigation" in t, "Missing 'mitigation' field"


def test_has_summary(threat_model):
    """Threat model must include a summary section."""
    assert "summary" in threat_model


def test_report_has_executive_summary(threat_report):
    """Report must include an executive summary."""
    lower = threat_report.lower()
    assert "executive summary" in lower or "summary" in lower


def test_report_has_architecture_overview(threat_report):
    """Report must include architecture overview."""
    lower = threat_report.lower()
    assert "architecture" in lower


def test_report_mentions_mitigations(threat_report):
    """Report must include mitigation recommendations."""
    lower = threat_report.lower()
    assert "mitigation" in lower or "recommendation" in lower


def test_mitigations_are_specific(threat_model):
    """Mitigations must be actionable (more than 10 chars each)."""
    for t in threat_model["threats"]:
        mitigation = t.get("mitigation", "")
        assert len(mitigation) > 10, (
            f"Mitigation too vague for threat on {t.get('component')}: '{mitigation}'"
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
    path = workspace / "architecture.json"
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
    path = workspace / "architecture.json"
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
    path = workspace / "architecture.json"
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
