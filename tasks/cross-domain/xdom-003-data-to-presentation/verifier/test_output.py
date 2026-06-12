"""Verifier for xdom-003: Data to Presentation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def presentation(workspace):
    path = workspace / "presentation.md"
    assert path.exists(), "presentation.md not found"
    return path.read_text()


@pytest.fixture
def charts_data(workspace):
    path = workspace / "charts_data.json"
    assert path.exists(), "charts_data.json not found"
    with open(path) as f:
        return json.load(f)


def test_presentation_exists(workspace):
    """presentation.md must exist."""
    assert (workspace / "presentation.md").exists()


def test_charts_data_exists(workspace):
    """charts_data.json must exist."""
    assert (workspace / "charts_data.json").exists()


def test_presentation_has_all_quarters(presentation):
    """Presentation must cover Q1 through Q4."""
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        assert q in presentation, f"{q} not found in presentation"


def test_presentation_has_slide_separators(presentation):
    """Presentation must use --- as slide separators."""
    assert "---" in presentation, "No slide separators (---) found"
    # At least 4 separators (title + 4 quarters + summary = 5 separators minimum-ish)
    assert presentation.count("---") >= 4, "Expected at least 4 slide separators"


def test_presentation_has_title_slide(presentation):
    """Presentation must have a title slide."""
    # First heading should be a title
    lines = presentation.strip().split("\n")
    assert any(line.startswith("# ") for line in lines[:5]), "No title heading found"


def test_presentation_has_summary(presentation):
    """Presentation must have a summary or trends slide."""
    lower = presentation.lower()
    assert "summary" in lower or "trend" in lower or "overview" in lower, \
        "No summary/trends slide found"


def test_charts_data_has_quarterly_revenue(charts_data):
    """charts_data must have quarterly_revenue with correct structure."""
    assert "quarterly_revenue" in charts_data
    qr = charts_data["quarterly_revenue"]
    assert "labels" in qr and "values" in qr
    assert len(qr["labels"]) == 4
    assert len(qr["values"]) == 4
    assert all(isinstance(v, (int, float)) for v in qr["values"])


def test_charts_data_has_quarterly_units(charts_data):
    """charts_data must have quarterly_units with correct structure."""
    assert "quarterly_units" in charts_data
    qu = charts_data["quarterly_units"]
    assert "labels" in qu and "values" in qu
    assert len(qu["labels"]) == 4
    assert len(qu["values"]) == 4
    assert all(isinstance(v, (int, float)) for v in qu["values"])


def test_charts_data_has_regional_revenue(charts_data):
    """charts_data must have regional_revenue."""
    assert "regional_revenue" in charts_data
    rr = charts_data["regional_revenue"]
    assert "labels" in rr and "values" in rr
    assert len(rr["labels"]) >= 3, "Expected at least 3 regions"
    assert len(rr["values"]) == len(rr["labels"])


def test_quarterly_revenue_values_reasonable(charts_data):
    """Quarterly revenue values must be computed from data (within tolerance)."""
    # Expected: Q1=261500, Q2=304200, Q3=338000, Q4=372300
    expected = [261500, 304200, 338000, 372300]
    actual = charts_data["quarterly_revenue"]["values"]
    for i, (exp, act) in enumerate(zip(expected, actual)):
        tolerance = exp * 0.02  # 2% tolerance
        assert abs(act - exp) <= tolerance, \
            f"Q{i+1} revenue: expected ~{exp}, got {act}"


def test_quarterly_units_values_reasonable(charts_data):
    """Quarterly unit values must be computed from data (within tolerance)."""
    # Expected: Q1=913, Q2=1052, Q3=1163, Q4=1275
    expected = [913, 1052, 1163, 1275]
    actual = charts_data["quarterly_units"]["values"]
    for i, (exp, act) in enumerate(zip(expected, actual)):
        tolerance = exp * 0.02
        assert abs(act - exp) <= tolerance, \
            f"Q{i+1} units: expected ~{exp}, got {act}"


def test_revenue_shows_growth(charts_data):
    """Revenue should show growth from Q1 to Q4."""
    values = charts_data["quarterly_revenue"]["values"]
    assert values[-1] > values[0], "Q4 revenue should be higher than Q1"


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
    path = workspace / "charts_data.json"
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
    path = workspace / "charts_data.json"
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
    path = workspace / "quarterly_data.csv"
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
