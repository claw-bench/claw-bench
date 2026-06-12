"""Verifier for xdom-007: Multi-format Document Conversion."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report_html(workspace):
    path = workspace / "report.html"
    assert path.exists(), "report.html not found"
    return path.read_text()


def test_report_exists(workspace):
    """report.html must exist."""
    assert (workspace / "report.html").exists()


def test_valid_html_structure(report_html):
    """HTML must have DOCTYPE, html, head, and body tags."""
    lower = report_html.lower()
    assert "<!doctype html>" in lower, "Missing <!DOCTYPE html>"
    assert "<html" in lower, "Missing <html> tag"
    assert "<head>" in lower or "<head " in lower, "Missing <head> tag"
    assert "<body>" in lower or "<body " in lower, "Missing <body> tag"
    assert "</html>" in lower, "Missing closing </html>"


def test_has_title(report_html):
    """HTML must have a <title> element."""
    lower = report_html.lower()
    assert "<title>" in lower and "</title>" in lower, "Missing <title> element"


def test_csv_data_as_table(report_html):
    """CSV data must be rendered as an HTML table with thead and tbody."""
    lower = report_html.lower()
    assert "<table" in lower, "Missing <table> element"
    assert "<thead>" in lower or "<thead " in lower, "Missing <thead>"
    assert "<tbody>" in lower or "<tbody " in lower, "Missing <tbody>"


def test_table_contains_csv_data(report_html):
    """Table must contain data from the CSV file."""
    assert "Alice Chen" in report_html, "Missing Alice Chen from CSV"
    assert "Bob Martinez" in report_html, "Missing Bob Martinez from CSV"
    assert "Engineering" in report_html, "Missing Engineering department"
    assert "alice@company.com" in report_html, "Missing email data"


def test_all_csv_rows_present(report_html):
    """All 7 team members from CSV must be in the report."""
    names = ["Alice Chen", "Bob Martinez", "Carol Kim", "Dave Patel",
             "Eve Johnson", "Frank Liu", "Grace Taylor"]
    for name in names:
        assert name in report_html, f"Missing team member: {name}"


def test_markdown_content_present(report_html):
    """Markdown content must be converted and included."""
    assert "Sprint Goals" in report_html or "sprint goals" in report_html.lower()
    assert "Key Decisions" in report_html or "key decisions" in report_html.lower()
    assert "PostgreSQL" in report_html, "Missing PostgreSQL content from notes"


def test_markdown_lists_converted(report_html):
    """Markdown lists should be converted to HTML lists."""
    lower = report_html.lower()
    assert "<li>" in lower, "No list items found - markdown lists not converted"
    assert "<ul>" in lower or "<ol>" in lower, "No list elements found"


def test_json_config_present(report_html):
    """JSON configuration data must be included in the report."""
    assert "Project Phoenix" in report_html, "Missing project name from config"
    assert "2.1.0" in report_html, "Missing version from config"
    assert "production" in report_html, "Missing environment from config"


def test_json_deployment_info(report_html):
    """Deployment configuration from JSON must be included."""
    assert "aws-east-1" in report_html, "Missing deployment target"


def test_has_sections(report_html):
    """Report should use section elements or clear heading structure."""
    lower = report_html.lower()
    has_sections = "<section" in lower
    has_headings = lower.count("<h2") >= 2 or lower.count("<h3") >= 2
    assert has_sections or has_headings, "Report should have sections or multiple headings"


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
    path = workspace / "source/config.json"
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
    path = workspace / "source/config.json"
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
    path = workspace / "source/data.csv"
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
