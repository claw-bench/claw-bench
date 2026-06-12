"""Verifier for web-008: Website Structure Mapping."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def sitemap(workspace):
    path = workspace / "sitemap.json"
    assert path.exists(), "sitemap.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def broken(workspace):
    path = workspace / "broken_links.json"
    assert path.exists(), "broken_links.json not found"
    return json.loads(path.read_text())


def test_sitemap_exists(workspace):
    assert (workspace / "sitemap.json").exists()


def test_broken_links_exists(workspace):
    assert (workspace / "broken_links.json").exists()


def test_total_pages(sitemap):
    assert sitemap["total_pages"] == 10


def test_all_pages_in_sitemap(sitemap):
    files = {p["file"] for p in sitemap["pages"]}
    expected = {"index.html", "about.html", "products.html", "services.html",
                "blog.html", "contact.html", "team.html", "pricing.html",
                "faq.html", "support.html"}
    assert files == expected


def test_pages_have_required_fields(sitemap):
    for page in sitemap["pages"]:
        assert "file" in page
        assert "title" in page
        assert "path" in page
        assert "links_to" in page
        assert "linked_from" in page


def test_index_path(sitemap):
    index = [p for p in sitemap["pages"] if p["file"] == "index.html"][0]
    assert index["path"] == "/"


def test_index_links_to(sitemap):
    index = [p for p in sitemap["pages"] if p["file"] == "index.html"][0]
    assert "/" in index["links_to"]
    assert "/about" in index["links_to"]
    assert "/products" in index["links_to"]


def test_home_linked_from_many(sitemap):
    index = [p for p in sitemap["pages"] if p["file"] == "index.html"][0]
    assert len(index["linked_from"]) >= 8, "Home should be linked from most pages"


def test_broken_links_count(broken):
    assert broken["total_broken"] == 7


def test_broken_links_include_expected(broken):
    broken_hrefs = {b["link_href"] for b in broken["broken"]}
    expected_broken = {"/blog/post-1", "/blog/post-2", "/careers",
                       "/docs", "/products/gadget", "/products/widget", "/status"}
    assert broken_hrefs == expected_broken


def test_broken_links_have_source(broken):
    for b in broken["broken"]:
        assert "source_file" in b
        assert "link_href" in b
        assert "reason" in b


def test_total_internal_links(sitemap):
    assert sitemap["total_internal_links"] >= 30


def test_contact_linked_from_many(sitemap):
    contact = [p for p in sitemap["pages"] if p["file"] == "contact.html"][0]
    assert len(contact["linked_from"]) >= 4


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
    path = workspace / "sitemap.json"
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
    path = workspace / "sitemap.json"
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
    path = workspace / "sitemap.json"
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
