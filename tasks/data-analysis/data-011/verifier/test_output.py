"""Verifier for data-011: Comprehensive Analysis Report."""

from pathlib import Path
import json
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    path = workspace / "report.md"
    assert path.exists(), "report.md not found"
    return path.read_text()


@pytest.fixture
def charts(workspace):
    path = workspace / "charts_data.json"
    assert path.exists(), "charts_data.json not found"
    return json.loads(path.read_text())


def test_report_file_exists(workspace):
    assert (workspace / "report.md").exists()


def test_charts_file_exists(workspace):
    assert (workspace / "charts_data.json").exists()


def test_report_has_summary_section(report):
    assert "Summary Statistics" in report or "summary statistics" in report.lower()


def test_report_has_top_performers(report):
    lower = report.lower()
    assert "top performers" in lower or "top 5" in lower


def test_report_has_regional_trends(report):
    lower = report.lower()
    assert "regional" in lower or "region" in lower


def test_report_has_quarterly_trends(report):
    lower = report.lower()
    assert "quarterly" in lower or "quarter" in lower


def test_report_has_recommendations(report):
    lower = report.lower()
    assert "recommendation" in lower


def test_report_contains_top_companies(report):
    top_names = ["BetaCorp", "IotaLabs", "EpsilonLtd", "GammaSoft", "DeltaInc"]
    found = sum(1 for name in top_names if name in report)
    assert found >= 3, f"Expected at least 3 of top 5 companies mentioned, found {found}"


def test_charts_has_three_types(charts):
    assert "bar_chart" in charts, "Missing bar_chart"
    assert "line_chart" in charts, "Missing line_chart"
    assert "pie_chart" in charts, "Missing pie_chart"


def test_charts_have_labels_and_values(charts):
    for chart_type in ["bar_chart", "line_chart", "pie_chart"]:
        assert "labels" in charts[chart_type], f"{chart_type} missing labels"
        assert "values" in charts[chart_type], f"{chart_type} missing values"
        assert len(charts[chart_type]["labels"]) == len(charts[chart_type]["values"]),             f"{chart_type} labels/values length mismatch"


def test_line_chart_quarterly(charts):
    labels = charts["line_chart"]["labels"]
    assert len(labels) == 4, f"Expected 4 quarters in line chart, got {len(labels)}"


def test_bar_chart_regions(charts):
    labels = charts["bar_chart"]["labels"]
    assert len(labels) == 4, f"Expected 4 regions in bar chart, got {len(labels)}"


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
    path = workspace / "charts_data.json"
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
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "company_data.csv"
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
