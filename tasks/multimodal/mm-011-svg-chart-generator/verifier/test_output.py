"""Verifier for mm-011: SVG Bar Chart Generator."""

import re
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def svg_content(workspace):
    path = workspace / "chart.svg"
    assert path.exists(), "chart.svg not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    assert (workspace / "chart.svg").exists()


def test_svg_root_element(svg_content):
    assert "<svg" in svg_content, "Must have an <svg> root element"
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg_content, "Must have SVG namespace"


def test_has_title(svg_content):
    assert "Sales by Region" in svg_content, "Must contain chart title 'Sales by Region'"


def test_title_is_text_element(svg_content):
    pattern = r"<text[^>]*>.*?Sales by Region.*?</text>"
    assert re.search(pattern, svg_content, re.DOTALL), "Title must be in a <text> element"


def test_has_six_rect_elements(svg_content):
    rects = re.findall(r"<rect\b", svg_content)
    assert len(rects) == 6, f"Expected 6 <rect> elements, got {len(rects)}"


def test_rect_elements_have_height(svg_content):
    rects = re.findall(r"<rect[^>]*>", svg_content)
    for rect in rects:
        assert 'height="' in rect, f"<rect> missing height attribute: {rect}"
        height_match = re.search(r'height="([^"]+)"', rect)
        height_val = float(height_match.group(1))
        assert height_val > 0, f"Bar height must be positive, got {height_val}"


def test_has_all_labels(svg_content):
    labels = ["North", "South", "East", "West", "Central", "Overseas"]
    for label in labels:
        pattern = rf"<text[^>]*>{label}</text>"
        assert re.search(pattern, svg_content), f"Missing label '{label}' in a <text> element"


def test_bars_proportional_heights(svg_content):
    """Bars should have heights proportional to their values."""
    rects = re.findall(r"<rect[^>]*>", svg_content)
    heights = []
    for rect in rects:
        h = re.search(r'height="([^"]+)"', rect)
        heights.append(float(h.group(1)))
    # East (150) should have tallest bar, Overseas (60) shortest
    assert max(heights) == heights[2], "East (index 2) should be tallest"
    assert min(heights) == heights[5], "Overseas (index 5) should be shortest"


def test_svg_closes(svg_content):
    assert "</svg>" in svg_content, "SVG must have closing </svg> tag"


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
    path = workspace / "chart_data.json"
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
    path = workspace / "chart_data.json"
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
    path = workspace / "chart_data.json"
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
