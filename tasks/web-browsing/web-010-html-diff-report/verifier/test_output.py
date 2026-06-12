"""Verifier for web-010: HTML Diff Report."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def diff_report(workspace):
    """Read and parse diff_report.json."""
    path = workspace / "diff_report.json"
    assert path.exists(), "diff_report.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """diff_report.json must exist in the workspace."""
    assert (workspace / "diff_report.json").exists()


def test_valid_json(workspace):
    """diff_report.json must be valid JSON."""
    path = workspace / "diff_report.json"
    try:
        json.loads(path.read_text())
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON: {e}")


def test_has_required_top_level_keys(diff_report):
    """Report must have added_elements, removed_elements, modified_elements."""
    assert "added_elements" in diff_report, "Missing 'added_elements' key"
    assert "removed_elements" in diff_report, "Missing 'removed_elements' key"
    assert "modified_elements" in diff_report, "Missing 'modified_elements' key"


def test_all_entries_have_required_fields(diff_report):
    """Every element entry must have tag, id, class, description."""
    for category in ["added_elements", "removed_elements", "modified_elements"]:
        for i, elem in enumerate(diff_report[category]):
            for field in ["tag", "id", "class", "description"]:
                assert field in elem, (
                    f"{category}[{i}] missing field '{field}'"
                )


def _find_element(elements, **kwargs):
    """Find an element matching the given criteria."""
    for el in elements:
        match = True
        for key, val in kwargs.items():
            if key == "description_contains":
                if val.lower() not in el.get("description", "").lower():
                    match = False
            elif el.get(key) != val:
                match = False
        if match:
            return el
    return None


# --- Added Elements Tests ---

def test_announcement_bar_added(diff_report):
    """The announcement-bar div should be detected as added."""
    el = _find_element(diff_report["added_elements"], id="announcement-bar")
    if not el:
        el = _find_element(diff_report["added_elements"], description_contains="announcement")
    assert el is not None, "announcement-bar element not found in added_elements"


def test_newsletter_section_added(diff_report):
    """The newsletter section should be detected as added."""
    el = _find_element(diff_report["added_elements"], id="newsletter")
    if not el:
        el = _find_element(diff_report["added_elements"], description_contains="newsletter")
    assert el is not None, "newsletter section not found in added_elements"


def test_product_4_added(diff_report):
    """Product-4 (MegaTool Elite) should be detected as added."""
    el = _find_element(diff_report["added_elements"], id="product-4")
    if not el:
        el = _find_element(diff_report["added_elements"], description_contains="MegaTool")
    assert el is not None, "product-4 element not found in added_elements"


def test_cta_button_added(diff_report):
    """The CTA button in the hero section should be detected as added."""
    el = _find_element(diff_report["added_elements"], id="cta-button")
    if not el:
        el = _find_element(diff_report["added_elements"], description_contains="Shop Now")
    if not el:
        el = _find_element(diff_report["added_elements"], tag="a", description_contains="cta")
    assert el is not None, "CTA button not found in added_elements"


# --- Removed Elements Tests ---

def test_product_3_removed(diff_report):
    """Product-3 (Sprocket Basic) should be detected as removed."""
    el = _find_element(diff_report["removed_elements"], id="product-3")
    if not el:
        el = _find_element(diff_report["removed_elements"], description_contains="Sprocket")
    assert el is not None, "product-3 element not found in removed_elements"


def test_old_disclaimer_removed(diff_report):
    """The old-disclaimer paragraph should be detected as removed."""
    el = _find_element(diff_report["removed_elements"], id="old-disclaimer")
    if not el:
        el = _find_element(diff_report["removed_elements"], description_contains="disclaimer")
    assert el is not None, "old-disclaimer element not found in removed_elements"


# --- Modified Elements Tests ---

def test_site_title_modified(diff_report):
    """The site-title h1 should be detected as modified (text changed)."""
    el = _find_element(diff_report["modified_elements"], id="site-title")
    if not el:
        el = _find_element(diff_report["modified_elements"], description_contains="Acme Corporation")
    assert el is not None, "site-title not found in modified_elements"
    desc = el.get("description", "").lower()
    assert "change" in desc or "modif" in desc or "text" in desc or "partners" in desc, (
        f"site-title description should mention the change: {el['description']}"
    )


def test_product_1_modified(diff_report):
    """Product-1 should be modified (name changed to Widget Pro X, price changed)."""
    el = _find_element(diff_report["modified_elements"], id="product-1")
    if not el:
        el = _find_element(diff_report["modified_elements"], description_contains="Widget Pro")
    assert el is not None, "product-1 not found in modified_elements"


def test_price_changes_detected(diff_report):
    """At least one product price change should be detected.

    The HTML has two price changes ($49.99->$59.99 and $79.99->$89.99).
    Accept detection of either one since implementations may handle
    duplicate-keyed elements differently.
    """
    found = False
    for el in diff_report["modified_elements"]:
        desc = el.get("description", "").lower()
        eid = el.get("id", "")
        ecls = el.get("class", "")
        # Match by product id, price class, or price values in description
        if eid in ("product-1", "product-2"):
            found = True
            break
        if "price" in ecls:
            found = True
            break
        if any(p in desc for p in ["49.99", "59.99", "79.99", "89.99"]):
            found = True
            break
    assert found, "No product price change detected in modified_elements"


def test_hero_section_modified(diff_report):
    """The hero section should be detected as modified (class and text changes)."""
    el = _find_element(diff_report["modified_elements"], id="hero")
    if not el:
        el = _find_element(diff_report["modified_elements"], description_contains="hero")
    assert el is not None, "hero section not found in modified_elements"


def test_copyright_modified(diff_report):
    """The copyright text should be detected as modified (2023 -> 2024)."""
    el = _find_element(diff_report["modified_elements"], description_contains="2024")
    if not el:
        el = _find_element(diff_report["modified_elements"], description_contains="copyright")
    assert el is not None, "copyright modification not found in modified_elements"


def test_no_empty_descriptions(diff_report):
    """No element entry should have an empty description."""
    for category in ["added_elements", "removed_elements", "modified_elements"]:
        for i, elem in enumerate(diff_report[category]):
            assert elem.get("description", "").strip(), (
                f"{category}[{i}] has empty description"
            )


def test_added_has_at_least_3_elements(diff_report):
    """There should be at least 3 added elements detected."""
    assert len(diff_report["added_elements"]) >= 3, (
        f"Expected at least 3 added elements, got {len(diff_report['added_elements'])}"
    )


def test_removed_has_at_least_2_elements(diff_report):
    """There should be at least 2 removed elements detected."""
    assert len(diff_report["removed_elements"]) >= 2, (
        f"Expected at least 2 removed elements, got {len(diff_report['removed_elements'])}"
    )


def test_modified_has_at_least_3_elements(diff_report):
    """There should be at least 3 modified elements detected."""
    assert len(diff_report["modified_elements"]) >= 3, (
        f"Expected at least 3 modified elements, got {len(diff_report['modified_elements'])}"
    )


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
    path = workspace / "diff_report.json"
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
    path = workspace / "diff_report.json"
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
    path = workspace / "diff_report.json"
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
