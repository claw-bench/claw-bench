"""Verifier for mm-012: HTML Report from Mixed Sources."""

import re
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def html_content(workspace):
    path = workspace / "combined_report.html"
    assert path.exists(), "combined_report.html not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    assert (workspace / "combined_report.html").exists()


def test_has_doctype(html_content):
    assert "<!DOCTYPE html>" in html_content or "<!doctype html>" in html_content.lower()


def test_has_title_element(html_content):
    assert re.search(r"<title>.*?Q3 2025 Performance Report.*?</title>", html_content, re.DOTALL), \
        "Must have <title> with report title from metadata"


def test_has_metadata_author(html_content):
    assert "Jane Morrison" in html_content, "Must include author from metadata"


def test_has_metadata_date(html_content):
    assert "2025-10-15" in html_content, "Must include date from metadata"


def test_has_metadata_department(html_content):
    assert "Strategic Planning" in html_content, "Must include department from metadata"


def test_has_summary_text(html_content):
    assert "Q3 performance exceeded expectations" in html_content, "Must include summary text"
    assert "competitive advantage" in html_content, "Must include full summary text"


def test_summary_in_paragraph(html_content):
    pattern = r"<p>.*?Q3 performance exceeded expectations.*?</p>"
    assert re.search(pattern, html_content, re.DOTALL), "Summary must be wrapped in <p> tags"


def test_has_html_table(html_content):
    assert "<table" in html_content, "Must contain an HTML table"
    assert "</table>" in html_content, "Table must be properly closed"


def test_table_has_headers(html_content):
    th_matches = re.findall(r"<th[^>]*>(.*?)</th>", html_content)
    th_texts = [t.strip() for t in th_matches]
    assert "Division" in th_texts, "Table must have 'Division' header"
    assert "Revenue" in th_texts, "Table must have 'Revenue' header"
    assert "Growth" in th_texts, "Table must have 'Growth' header"
    assert "Headcount" in th_texts, "Table must have 'Headcount' header"


def test_table_has_data_rows(html_content):
    td_matches = re.findall(r"<td[^>]*>(.*?)</td>", html_content)
    td_texts = [t.strip() for t in td_matches]
    assert "Cloud Services" in td_texts, "Table must include Cloud Services row"
    assert "Enterprise" in td_texts, "Table must include Enterprise row"
    assert "Consumer" in td_texts, "Table must include Consumer row"
    assert "Consulting" in td_texts, "Table must include Consulting row"
    assert "Support" in td_texts, "Table must include Support row"


def test_table_row_count(html_content):
    """Should have 5 data rows plus 1 header row = at least 6 <tr> elements."""
    tr_matches = re.findall(r"<tr", html_content)
    assert len(tr_matches) >= 6, f"Expected at least 6 <tr> elements, got {len(tr_matches)}"


def test_has_section_headings(html_content):
    h_tags = re.findall(r"<h[12][^>]*>", html_content)
    assert len(h_tags) >= 3, f"Expected at least 3 heading elements, got {len(h_tags)}"


def test_has_revenue_values(html_content):
    assert "4500000" in html_content, "Must include Cloud Services revenue"
    assert "3200000" in html_content, "Must include Enterprise revenue"


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
    path = workspace / "metadata.json"
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
    path = workspace / "metadata.json"
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
    path = workspace / "data_table.csv"
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
