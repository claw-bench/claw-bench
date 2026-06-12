"""Verifier for web-009: RSS Feed Parser."""

import json
from pathlib import Path
from email.utils import parsedate_to_datetime

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def feed_items(workspace):
    """Read and parse feed_items.json."""
    path = workspace / "feed_items.json"
    assert path.exists(), "feed_items.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """feed_items.json must exist in the workspace."""
    assert (workspace / "feed_items.json").exists()


def test_valid_json(workspace):
    """feed_items.json must be valid JSON."""
    path = workspace / "feed_items.json"
    try:
        json.loads(path.read_text())
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON: {e}")


def test_correct_item_count(feed_items):
    """There should be exactly 8 items parsed from the feed."""
    assert len(feed_items) == 8, f"Expected 8 items, got {len(feed_items)}"


def test_items_are_objects_with_required_fields(feed_items):
    """Each item must have title, link, pubDate, description."""
    for i, item in enumerate(feed_items):
        for field in ["title", "link", "pubDate", "description"]:
            assert field in item, f"Item {i} missing field '{field}'"


def test_sorted_by_date_descending(feed_items):
    """Items must be sorted by pubDate in descending order."""
    dates = []
    for item in feed_items:
        dt = parsedate_to_datetime(item["pubDate"])
        dates.append(dt)
    for i in range(len(dates) - 1):
        assert dates[i] >= dates[i + 1], (
            f"Items not sorted descending: '{feed_items[i]['pubDate']}' should be >= '{feed_items[i+1]['pubDate']}'"
        )


def test_first_item_is_newest(feed_items):
    """The first item should be the quantum computing article (Fri 20 Sep 14:30)."""
    assert "Quantum Computing" in feed_items[0]["title"]


def test_last_item_is_oldest(feed_items):
    """The last item should be the climate pledge article (Sun 15 Sep)."""
    assert "Climate" in feed_items[-1]["title"]


def test_all_titles_present(feed_items):
    """All 8 article titles must be present."""
    titles = [item["title"] for item in feed_items]
    expected_keywords = [
        "Quantum",
        "AI Regulation",
        "Satellite",
        "Security Vulnerability",
        "Battery Recycling",
        "Flux",
        "Healthcare AI",
        "Climate",
    ]
    for keyword in expected_keywords:
        found = any(keyword in title for title in titles)
        assert found, f"No item title contains '{keyword}'"


def test_all_links_present(feed_items):
    """All items must have valid links starting with https://."""
    for item in feed_items:
        assert item["link"].startswith("https://"), (
            f"Invalid link: {item['link']}"
        )


def test_descriptions_have_no_html_tags(feed_items):
    """Descriptions must not contain HTML tags."""
    import re
    for item in feed_items:
        desc = item["description"]
        tags = re.findall(r'<[a-zA-Z/][^>]*>', desc)
        assert len(tags) == 0, (
            f"HTML tags found in description of '{item['title']}': {tags}"
        )


def test_description_content_preserved(feed_items):
    """Key content from descriptions must survive HTML stripping."""
    all_descs = " ".join(item["description"] for item in feed_items)
    assert "1000-qubit" in all_descs
    assert "CVE-2024-8842" in all_descs
    assert "94%" in all_descs or "94% accuracy" in all_descs
    assert "$10 billion" in all_descs
    assert "GreenCycle" in all_descs
    assert "100,000 GitHub stars" in all_descs


def test_pub_dates_are_rfc2822(feed_items):
    """All pubDate values must be parseable as RFC 2822 dates."""
    for item in feed_items:
        try:
            parsedate_to_datetime(item["pubDate"])
        except Exception as e:
            pytest.fail(f"Cannot parse pubDate '{item['pubDate']}': {e}")


def test_ev_battery_before_quantum_same_day(feed_items):
    """On Sep 20, quantum (14:30) should be before EV battery (08:00) since descending."""
    titles = [item["title"] for item in feed_items]
    quantum_idx = next(i for i, t in enumerate(titles) if "Quantum" in t)
    ev_idx = next(i for i, t in enumerate(titles) if "Battery" in t)
    assert quantum_idx < ev_idx, (
        "Quantum (14:30 GMT) should appear before EV Battery (08:00 GMT) in descending order"
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
    path = workspace / "feed_items.json"
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
    path = workspace / "feed_items.json"
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
    path = workspace / "feed_items.json"
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
